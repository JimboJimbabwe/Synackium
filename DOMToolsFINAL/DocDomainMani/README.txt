To use this scanner:

Copy the entire code above and paste it into your browser's console

Start the scanner:

const domainMonitor = findDocumentDomainVulns();

To stop monitoring:

domainMonitor.stopMonitoring();

his scanner will:

Monitor all attempts to modify document.domain
Check for scripts that manipulate document.domain
Look for dynamic script additions that might modify the domain
Check URL parameters that might be used for domain manipulation
Track the call stack when document.domain is modified

You can check findings at any time:

console.table(domainMonitor.findings);

The scanner specifically looks for:

Direct document.domain modifications
Suspicious scripts containing domain manipulation
Dynamic script additions that might modify domain
URL parameters that could be used in domain manipulation
Parent/child domain relationships that might be exploitable