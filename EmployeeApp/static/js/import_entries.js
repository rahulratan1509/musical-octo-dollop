document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    const progressBar = document.querySelector('.progress-bar');
    const statusMessage = document.querySelector('#status-message');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(form);

        try {
            const response = await fetch('{% url "import_entries" %}', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',  // Add this header for AJAX requests
                },
            });

            if (!response.ok) {
                throw new Error('Import failed');
            }

            // Handle the response, e.g., display a success message
            const result = await response.json();
            statusMessage.textContent = `Import successful! ${result.created} entries created.`;
        } catch (error) {
            statusMessage.textContent = 'Import failed. Please check the file format and try again.';
        }
    });
});
