// To swallow greedily

// Function to pause execution
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

// Keep track of what we've already processed
const processedHrefs = new Set();
let allData = [];

// Function to extract data
async function extractTargetData() {
    const targetItems = document.querySelectorAll('a.targets-list-item');
    
    for (const item of targetItems) {
        const href = item.getAttribute('href');
        
        // Skip if we've already processed this href
        if (processedHrefs.has(href)) continue;
        
        await sleep(100);
        const codenameHeader = item.querySelector('h4.target-tooltip-codename-header');
        const codename = codenameHeader ? codenameHeader.textContent.trim() : 'No codename found';
        
        if (href && codename !== 'No codename found') {
            allData.push({ href, codename });
            processedHrefs.add(href);
            console.log(`New item found: ${href} -> ${codename}`);
            console.log('Total unique items so far:', allData.length);
        }
    }
}

// Create scroll listener with debounce
let scrollTimeout;
window.addEventListener('scroll', () => {
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
        extractTargetData();
    }, 300);  // Wait 300ms after scrolling stops before extracting
});

// Initial extraction
console.log('Starting extraction - scroll to find more items...');
extractTargetData();

// Function to get current results anytime
function getResults() {
    console.log('Current results:', JSON.stringify(allData, null, 2));
    console.log('Total unique items:', allData.length);
    return allData;
}
