@echo off
echo Starting WC Control System...
echo MQTT Handler will be initialized...
echo Web interface will be available at: http://localhost:5000
echo Dashboard: http://localhost:5000
echo Simple UI: http://localhost:5000/simple  
echo Events: http://localhost:5000/events
echo.
echo ============================================================
python start_app.py
pause
