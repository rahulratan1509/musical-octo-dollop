document.addEventListener('DOMContentLoaded', function () {
    const deleteLinks = document.querySelectorAll('.delete-link');

    deleteLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const entryId = this.getAttribute('data-entry-id');
            const deleteForm = document.querySelector(`form[data-entry-id="${entryId}"]`);
            const confirmDelete = confirm('Are you sure you want to delete this entry?');

            console.log('JavaScript executed!'); // Ensure this line is executed

            if (confirmDelete && deleteForm) { // Add a check for deleteForm
                deleteForm.submit();
            }
        });
    });
});
