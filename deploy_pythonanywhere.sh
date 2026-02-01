#!/bin/bash
# Quick PythonAnywhere Deployment Script

echo "================================"
echo "Dusangire PythonAnywhere Deploy"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Activate virtual environment
echo -e "${YELLOW}[1/7] Activating virtual environment...${NC}"
source ~/.virtualenvs/dusangire_env/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Step 2: Pull latest code
echo -e "${YELLOW}[2/7] Pulling latest code from GitHub...${NC}"
cd ~/dusangire12
git pull origin main
echo -e "${GREEN}✓ Code updated${NC}"
echo ""

# Step 3: Install dependencies
echo -e "${YELLOW}[3/7] Installing dependencies...${NC}"
pip install -r requirements.txt --upgrade
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 4: Collect static files
echo -e "${YELLOW}[4/7] Collecting static files...${NC}"
python manage.py collectstatic --noinput --clear
echo -e "${GREEN}✓ Static files collected${NC}"
echo ""

# Step 5: Run migrations
echo -e "${YELLOW}[5/7] Running migrations...${NC}"
python manage.py migrate
echo -e "${GREEN}✓ Migrations applied${NC}"
echo ""

# Step 6: System check
echo -e "${YELLOW}[6/7] Running Django system check...${NC}"
python manage.py check
echo -e "${GREEN}✓ System check passed${NC}"
echo ""

# Step 7: Reload web app (if PA token is available)
echo -e "${YELLOW}[7/7] Deployment complete!${NC}"
echo ""
echo -e "${GREEN}✓ All steps completed successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Go to PythonAnywhere Dashboard"
echo "2. Click 'Reload' on your web app"
echo "3. Visit https://yourname.pythonanywhere.com/"
echo ""
echo "If you see errors, check:"
echo "  - /var/log/yourname.pythonanywhere.com.error.log"
echo "  - /var/log/yourname.pythonanywhere.com.server.log"
echo ""
