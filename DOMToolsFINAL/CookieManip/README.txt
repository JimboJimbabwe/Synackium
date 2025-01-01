To use this scanner:

Copy the entire code above and paste it into your browser's console
Start the scanner:

const cookieMonitor = findCookieManipulationVulns();

To stop monitoring cookie changes:

cookieMonitor.stopMonitoring();

This scanner will:

Check for scripts that directly manipulate cookies
Look for usage of location.hash with cookies
Monitor real-time cookie modifications
Inspect current cookies for suspicious values
Check URL parameters for potential cookie manipulation
Watch for dynamic cookie changes

The results will show:

Scripts accessing document.cookie
Suspicious patterns like hash-based manipulation
Dynamic cookie modifications as they happen
Current cookies with potentially injectable content
URL parameters that might be used in cookie manipulation