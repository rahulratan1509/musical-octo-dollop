// EmployeeApp/static/js/script.js
$(document).ready(function () {
  $('#branch-dropdown').change(function () {
    var selectedBranch = $(this).val();
    // Implement AJAX request to fetch and populate areas based on the selected branch
    $.ajax({
        url: '/ajax/load-areas/',
        data: {
            'branch': selectedBranch
        },
        dataType: 'json',
        success: function (data) {
            var areaDropdown = $('#area-dropdown');
            areaDropdown.empty();
            areaDropdown.append($('<option>').text('Select Area').attr('value', ''));
            $.each(data.areas, function (key, value) {
                areaDropdown.append($('<option>').text(value).attr('value', value));
            });
        }
    });
  });

  // Add similar code for other dropdowns
});
