To use this scanner:

Copy the entire code above and paste it into your browser's console
Start the scanner:

const sqlMonitor = findClientSQLInjectionVulns();

To stop monitoring:

sqlMonitor.stopMonitoring();

This scanner will detect:

WebSQL database operations
Unprepared SQL statements
SQL queries using string concatenation
Unsafe parameter handling
SQL-like patterns in scripts
Suspicious URL parameters

You can check findings at any time:

console.table(sqlMonitor.findings);
The scanner specifically looks for:

Direct use of executeSql without parameters
String concatenation in SQL queries
Template literals in queries
Unsafe input sources in queries
SQL keywords in scripts and URLs
Database operations