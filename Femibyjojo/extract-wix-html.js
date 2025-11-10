// Wix Site HTML Extractor
// Run this in your browser's Developer Console while viewing femibyjojo.com

// Wait for page to fully load
setTimeout(() => {
    // Extract the main content
    const content = {
        header: document.querySelector('#SITE_HEADER')?.outerHTML || 'Not found',
        navigation: document.querySelector('nav')?.outerHTML || 'Not found',
        mainContent: document.querySelector('#PAGES_CONTAINER')?.outerHTML || 'Not found',
        footer: document.querySelector('#SITE_FOOTER')?.outerHTML || 'Not found',
        allSections: []
    };

    // Get all main sections
    const sections = document.querySelectorAll('section, [data-mesh-id], .s_');
    sections.forEach((section, index) => {
        content.allSections.push({
            index: index,
            tagName: section.tagName,
            id: section.id,
            classes: section.className,
            html: section.outerHTML
        });
    });

    // Get all text content
    content.allText = document.body.innerText;

    // Get all links
    content.links = Array.from(document.querySelectorAll('a')).map(a => ({
        text: a.innerText,
        href: a.href
    }));

    // Get all images
    content.images = Array.from(document.querySelectorAll('img')).map(img => ({
        src: img.src,
        alt: img.alt
    }));

    // Get all buttons
    content.buttons = Array.from(document.querySelectorAll('button, [role="button"]')).map(btn => ({
        text: btn.innerText,
        id: btn.id,
        classes: btn.className
    }));

    // Save to file (will download)
    const dataStr = JSON.stringify(content, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'femibyjojo-extracted-content.json';
    link.click();

    // Also log to console
    console.log('=== EXTRACTED CONTENT ===');
    console.log(content);
    console.log('\n=== FULL PAGE HTML ===');
    console.log(document.documentElement.outerHTML);

    alert('Content extracted! Check your downloads for femibyjojo-extracted-content.json and check the console for the full HTML.');
}, 3000); // Wait 3 seconds for page to load

console.log('Extraction will begin in 3 seconds...');
