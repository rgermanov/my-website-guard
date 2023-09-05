// Articles:
// https://www.pluralsight.com/resources/blog/cloud/serverless-browser-automation-with-aws-lambda-and-puppeteer



const puppeteer = require('puppeteer');

const baseURL = 'https://redesign.marketvector.com';
let visitedLinks = new Set();
let errors = [];
let linkCounter = 0;

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


async function checkLink(page, url) {
    if (visitedLinks.has(url)) {
        return;
    }

    visitedLinks.add(url);
    
    await page.goto(url, { waitUntil: 'networkidle2' });

    const status = await page.evaluate(() => {
        return document.readyState;
    });

    if (status !== 'complete') {
        errors.push({url, status: 'Failed to load'});
    } else {
        const response = await page.goto(url);
        if (response.status() !== 200) {
            errors.push({url, status: response.status()});
        }
    }

    // Extract links on the current page and check them recursively.
    const links = await page.$$eval('a', (links, baseURL) => {
        return links.map(link => link.href).filter(href => href.startsWith(baseURL));
    }, baseURL);
    

    for (let link of links) {
        linkCounter++;
    
        // Skip non-HTML resources
        if (link.endsWith('.pdf') || link.endsWith('.jpg') || link.endsWith('.png') || link.endsWith('.gif') || link.endsWith('.zip')) {
            continue;
        }
    
        if (linkCounter % 10 === 0) {
            await sleep(500);  // Introduce a half-second delay every 10 link visits.
        }
    
        try {
            await checkLink(page, link);
        } catch (error) {
            console.error(`Error visiting ${link}:`, error.message);
        }
    }
    
}

(async () => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    await checkLink(page, baseURL);

    await browser.close();

    console.log("Visited Links:", visitedLinks);
    console.log("Error Links:", errors);
})();
