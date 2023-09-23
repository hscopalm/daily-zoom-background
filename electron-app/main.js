// require modules
const { app, BrowserWindow } = require('electron')
const path = require('node:path')
const cheerio = require("cheerio")
const axios = require("axios")


// downloading the target web page 
// by performing an HTTP GET request in Axios
async function getHolidays() {
    
    const axiosResponse = await axios.request({
        method: "GET",
        url: "https://nationaltoday.com/what-is-today/",
        headers: {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            }
    })

}

getHolidays()

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
