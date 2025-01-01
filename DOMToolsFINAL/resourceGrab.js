async function downloadResources() {
    // Get all resources
    const urls = performance.getEntriesByType("resource")
        .filter(res => res.name.includes("www.nba.com"))
        .map(res => res.name);
    
    // Create JSZip instance
    const zip = new JSZip();
    
    // Download each resource
    const downloads = urls.map(async url => {
        try {
            const response = await fetch(url);
            const blob = await response.blob();
            const filename = url.split('/').pop();
            zip.file(filename, blob);
        } catch (err) {
            console.log(`Failed to download: ${url}`);
        }
    });
    
    await Promise.all(downloads);
    
    // Generate and download zip
    const zipBlob = await zip.generateAsync({type: "blob"});
    const link = document.createElement('a');
    link.href = URL.createObjectURL(zipBlob);
    link.download = "resources.zip";
    link.click();
}

// First load JSZip
const script = document.createElement('script');
script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';
script.onload = downloadResources;
document.head.appendChild(script);

