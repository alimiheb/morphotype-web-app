(function() {
    'use strict';
    
    // Get analysis data from data attribute
    const analysisElement = document.getElementById('analysis-data');
    
    try {
        const analysisDataStr = analysisElement?.getAttribute('data-analysis');
        window.analysisData = analysisDataStr ? JSON.parse(analysisDataStr) : null;
    } catch (error) {
        console.error('Failed to parse analysis data:', error);
        window.analysisData = null;
    }
    
    // Make downloadResults function globally available
    window.downloadResults = function() {
        if (!window.analysisData) {
            alert('No analysis data available for download.');
            return;
        }
        
        // Future implementation for PDF generation
        alert('PDF download feature coming soon! For now, please use the print function.');
    };
})();