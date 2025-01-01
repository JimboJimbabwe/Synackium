To use this scanner:

Copy the entire code above and paste it into your browser's console
Start the scanner:

const jsonMonitor = findJSONInjectionVulns();

To stop monitoring:

jsonMonitor.stopMonitoring();

This scanner will detect:

JSON.parse() calls
jQuery.parseJSON() calls
Suspicious JSON patterns
Dynamic JSON parsing
Prototype pollution attempts
Constructor manipulation
Template literal usage in JSON
DOM object references in JSON

You can check findings at any time:

console.table(jsonMonitor.findings);
The scanner specifically looks for:

Prototype pollution attempts
Constructor access attempts
String concatenation in JSON
Template literals in JSON
DOM object references
Possible HTML injection
Function definitions
Eval usage