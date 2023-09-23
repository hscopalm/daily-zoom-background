// test file while practicing scraping portion

// import modules
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

    // parsing the HTML source of the target web page with Cheerio
    const $ = cheerio.load(axiosResponse.data)
    
    //  replicate this python logic
    // holidays= [] 
    // for element in soup.body.find_all('h3', class_= 'holiday-title'): # create list of holidays from tagged elements
    //     holidays.append(element.string)
    
    const holidays = []
    
    // find all h3 headers of class 'holiday-title'
    const headerHolidays = $('h3.holiday-title')
    
    // Iterate over each div element with a class of "example" and print its text content
    headerHolidays.each((i, div) => {
        console.log($(div).text());
    });

}

getHolidays()
