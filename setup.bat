@echo off
echo Setting up Streamlit configuration...

mkdir %USERPROFILE%\.streamlit 2> nul

echo [server] > %USERPROFILE%\.streamlit\config.toml
echo headless = true >> %USERPROFILE%\.streamlit\config.toml
echo port = %PORT% >> %USERPROFILE%\.streamlit\config.toml
echo enableCORS = false >> %USERPROFILE%\.streamlit\config.toml

echo Streamlit configuration created successfully!