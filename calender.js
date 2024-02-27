document.addEventListener('DOMContentLoaded', function() {
    var calenderElement = document.getElementById('calender');
    var calender =  FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        selectable: true,
        dateClick: function(info) {
            $('#date').val(info.dateStr); 
        }
});
 calender.render();
});