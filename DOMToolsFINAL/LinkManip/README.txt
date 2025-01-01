To use this scanner:

Copy the entire code above and paste it into your browser's console

Start the scanner:

const linkMonitor = findLinkManipulationVulns();

To stop monitoring:

linkMonitor.stopMonitoring();

This scanner will detect:

Dynamic modifications to href, src, and action attributes
Suspicious URL patterns (javascript:, data:, etc.)
Links and forms with dynamic targets
Event handlers that might modify links
Dynamic additions of links and forms
Potentially malicious redirections

You can check findings at any time:

console.table(linkMonitor.findings);
The scanner looks for:

Links containing dynamic JavaScript
Forms with dynamic action attributes
Suspicious URL schemes
Dynamic attribute modifications
Event handlers modifying link targets
Cross-domain redirections