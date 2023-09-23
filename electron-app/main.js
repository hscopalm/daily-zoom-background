// require modules
const { app, BrowserWindow } = require('electron')
const path = require('node:path')

// create browser window instance and load index.html
const createWindow = () => {
    const win = new BrowserWindow({
      width: 800,
      height: 600,
      webPreferences: {
        preload: path.join(__dirname, 'preload.js')
      }
    })
  
    win.loadFile('index.html')
  }

// actually create window once ready, and handle mac not actually quitting
app.whenReady().then(() => {
    createWindow()
  
    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
  })

// quit application if all windows are closed (win/linux)
  app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit()
  })
