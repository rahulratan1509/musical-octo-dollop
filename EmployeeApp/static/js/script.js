$(document).ready(function() {
    // Dummy data for branches and areas
    var branches = [
        { id: 1, name: 'Branch A' },
        { id: 2, name: 'Branch B' },
        // Add more branches as needed
    ];

    var areas = [
        { branchId: 1, name: 'Area 1' },
        { branchId: 1, name: 'Area 2' },
        { branchId: 2, name: 'Area 3' },
        // Add more areas as needed
    ];

    var branchDropdown = $('#branch-dropdown');
    var areaDropdown = $('#area-dropdown');

    // Populate branch dropdown
    branches.forEach(function(branch) {
        $('<option>', {
            value: branch.id,
            text: branch.name
        }).appendTo(branchDropdown);
    });

    // Update area dropdown based on selected branch
    branchDropdown.on('change', function() {
        var selectedBranchId = $(this).val();
        areaDropdown.empty().append($('<option>', {
            value: '',
            text: 'Select Area'
        }));

        areas.forEach(function(area) {
            if (area.branchId == selectedBranchId) {
                $('<option>', {
                    value: area.name,
                    text: area.name
                }).appendTo(areaDropdown);
            }
        });
    });

    // Password toggle functionality
    $('#password-toggle').on('change', function() {
        var passwordInput = $('#id_password');
        if (this.checked) {
            passwordInput.attr('type', 'text');
        } else {
            passwordInput.attr('type', 'password');
        }
    });
});
