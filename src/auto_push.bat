@echo off
:: ===== AUTO ADD + COMMIT + PUSH TO GITHUB =====

:: Lấy ngày giờ để tạo message commit tự động
for /f "delims=" %%a in ('git config user.name') do set username=%%a
set datetime=%date%_%time%

:: Add tất cả file
git add .

:: Commit
git commit -m "Auto commit by %username% on %datetime%"

:: Push lên branch hiện tại
git push
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
echo ---------------------------------------------
echo   Da push code len GitHub thanh cong!
echo ---------------------------------------------
pause