To use this scanner:

Copy the entire code above and paste it into your browser's console

Start the scanner:

const ajaxMonitor = findAjaxHeaderManipulationVulns();

To stop monitoring:

ajaxMonitor.stopMonitoring();

This scanner will detect:

All XMLHttpRequest operations
Custom headers being set
jQuery Ajax calls
jQuery.globalEval usage
Suspicious header modifications
Ajax request patterns

You can check findings at any time:

console.table(ajaxMonitor.findings);
The scanner specifically looks for:

Header manipulation in XMLHttpRequest
jQuery Ajax calls with custom headers
Use of potentially dangerous jQuery methods
Patterns of Ajax request manipulation
Suspicious header values
Stack traces for all Ajax operations