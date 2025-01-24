javascript:(function() {
    // Create UI overlay
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 10px;
        border-radius: 5px;
        z-index: 9999;
        font-family: monospace;
        max-width: 300px;
    `;
    document.body.appendChild(overlay);

    // Track current element
    let currentElement = null;

    // Highlight element on hover
    document.addEventListener('mousemove', (e) => {
        const element = document.elementFromPoint(e.clientX, e.clientY);
        if (element === currentElement) return;
        
        // Remove previous highlight
        if (currentElement) {
            currentElement.style.outline = currentElement._originalOutline;
        }

        currentElement = element;
        
        // Store original outline
        currentElement._originalOutline = currentElement.style.outline;
        
        // Add highlight
        currentElement.style.outline = '2px solid red';

        // Get computed styles
        const styles = window.getComputedStyle(element);
        
        // Display relevant CSS info
        overlay.innerHTML = `
            <strong>${element.tagName.toLowerCase()}</strong>
            ${element.id ? '#' + element.id : ''}
            ${Array.from(element.classList).map(c => '.' + c).join('')}
            <br><br>
            <strong>Size:</strong><br>
            Width: ${styles.width}<br>
            Height: ${styles.height}<br>
            Padding: ${styles.padding}<br>
            Margin: ${styles.margin}<br>
            <br>
            <strong>Visual:</strong><br>
            Background: ${styles.background}<br>
            Color: ${styles.color}<br>
            Font: ${styles.font}<br>
            Position: ${styles.position}
        `;
    });

    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.textContent = 'Close Analyzer';
    closeBtn.style.cssText = `
        position: fixed;
        top: 10px;
        left: 10px;
        z-index: 9999;
    `;
    closeBtn.onclick = () => {
        overlay.remove();
        closeBtn.remove();
        if (currentElement) {
            currentElement.style.outline = currentElement._originalOutline;
        }
    };
    document.body.appendChild(closeBtn);
})();
