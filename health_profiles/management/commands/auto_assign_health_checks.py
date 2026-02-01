"""
Management command to auto-assign pending health checks to available consultants
Usage: python manage.py auto_assign_health_checks
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from health_profiles.models import HealthCheck, ConsultantAvailability, AutoAssignmentLog
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Auto-assign pending health checks to available consultants'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Print detailed assignment information'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without actually making assignments'
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        # Get pending health checks
        pending_checks = HealthCheck.objects.filter(
            status='pending',
            assigned_consultant__isnull=True
        ).order_by('-priority', 'created_at')

        total = pending_checks.count()
        assigned = 0
        failed = 0

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"Auto-Assignment Report - {timezone.now()}")
        self.stdout.write(f"{'='*60}\n")
        self.stdout.write(f"Total pending health checks: {total}")

        if total == 0:
            self.stdout.write(self.style.SUCCESS('✓ No pending health checks to assign'))
            return

        # Group by priority
        priority_groups = {}
        for check in pending_checks:
            if check.priority not in priority_groups:
                priority_groups[check.priority] = []
            priority_groups[check.priority].append(check)

        # Get available consultants
        available_consultants = ConsultantAvailability.objects.filter(
            status='available'
        ).order_by('-average_rating', 'current_assignments')

        self.stdout.write(f"Available consultants: {available_consultants.count()}\n")

        # Assign by priority
        for priority in ['urgent', 'high', 'normal', 'low']:
            checks_for_priority = priority_groups.get(priority, [])
            if not checks_for_priority:
                continue

            self.stdout.write(f"\n{priority.upper()} Priority ({len(checks_for_priority)} checks):")
            self.stdout.write("-" * 60)

            for health_check in checks_for_priority:
                # Find best consultant
                best_consultant = self._find_best_consultant(health_check, available_consultants)

                if best_consultant:
                    if not dry_run:
                        success = self._assign_check(health_check, best_consultant)
                        if success:
                            assigned += 1
                            available_slots = best_consultant.available_slots - 1
                        else:
                            failed += 1
                            available_slots = best_consultant.available_slots
                    else:
                        assigned += 1
                        available_slots = best_consultant.available_slots

                    status_icon = "✓" if not dry_run or True else "→"
                    self.stdout.write(
                        f"  {status_icon} Check #{health_check.id}: Patient {health_check.patient.username} "
                        f"→ {best_consultant.consultant.get_full_name()} "
                        f"(Slots: {available_slots})"
                    )

                    if verbose:
                        self.stdout.write(f"    Type: {health_check.get_check_type_display()}")
                        self.stdout.write(f"    Description: {health_check.description[:50]}...")

                else:
                    self.stdout.write(
                        self.style.WARNING(f"  ✗ Check #{health_check.id}: No available consultant")
                    )

                    if not dry_run:
                        AutoAssignmentLog.objects.create(
                            health_check=health_check,
                            result='no_available',
                            message='No available consultant matching criteria'
                        )

        # Summary
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"SUMMARY")
        self.stdout.write(f"{'='*60}")
        self.stdout.write(f"Total processed: {total}")
        self.stdout.write(self.style.SUCCESS(f"Successfully assigned: {assigned}"))
        if failed > 0:
            self.stdout.write(self.style.WARNING(f"Failed assignments: {failed}"))
        self.stdout.write(f"Awaiting consultants: {total - assigned}")
        
        if dry_run:
            self.stdout.write(f"\n{self.style.WARNING('DRY RUN - No changes saved')}\n")
        else:
            self.stdout.write(f"\n{self.style.SUCCESS('✓ Auto-assignment complete')}\n")

    def _find_best_consultant(self, health_check, available_consultants):
        """Find best available consultant for a health check"""
        for consultant_avail in available_consultants:
            if not consultant_avail.is_available:
                continue

            # Check specialization match
            if consultant_avail.preferred_check_types:
                preferred_types = [t.strip() for t in consultant_avail.preferred_check_types.split(',')]
                if health_check.check_type not in preferred_types:
                    continue

            return consultant_avail

        return None

    def _assign_check(self, health_check, consultant_avail):
        """Assign health check to consultant"""
        try:
            consultant = consultant_avail.consultant

            # Update health check
            health_check.assigned_consultant = consultant
            health_check.status = 'assigned'
            health_check.auto_assigned = True
            health_check.assigned_at = timezone.now()
            health_check.assignment_reason = f"Auto-assigned to {consultant_avail.specialization}"
            health_check.save()

            # Update consultant availability
            consultant_avail.current_assignments += 1
            consultant_avail.save()

            # Log assignment
            AutoAssignmentLog.objects.create(
                health_check=health_check,
                assigned_consultant=consultant,
                result='success',
                message=f"Auto-assigned to {consultant.get_full_name()}"
            )

            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error assigning check: {str(e)}"))
            return False
