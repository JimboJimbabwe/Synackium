To use this scanner:

Copy the entire code above and paste it into your browser's console
Start the scanner:

const xpathMonitor = findXPathInjectionVulns();

To stop monitoring:

xpathMonitor.stopMonitoring();

This scanner will detect:

document.evaluate() calls
element.evaluate() calls
Suspicious XPath expressions
Dynamic XPath generation
XPath patterns in scripts
Suspicious URL parameters

You can check findings at any time:

console.table(xpathMonitor.findings);

The scanner specifically looks for:

String concatenation in XPath
Dynamic expression building
Use of location/document/window objects
Boolean operations that might indicate injection
Suspicious XPath patterns
URL parameters containing XPath-like syntax