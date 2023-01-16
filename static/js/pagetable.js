function pageing() {
    var startcounter, stopcounter, prevpage, nextpage, table, tr;
    prevpage = document.getElementById("prevpage");
    nextpage = document.getElementById("nextpage");
    table = document.getElementById("tableoffallcustomers");
    tr = table.getElementsByTagName("tr");
    stopcounter = 10;
    startcounter = 0;
    for (i = 0; i < tr.length; i++) {
        if (i <= stopcounter) {
            if (i >= startcounter) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }


    }

    function searchtable() {
        var input, filter, table, tr, td, i, txtValue;
        input = document.getElementById("searchbar");
        filter = input.value.toUpperCase();
        table = document.getElementById("tableoffallcustomers");
        tr = table.getElementsByTagName("tr");


        for (i = 0; i < tr.length; i++) {
            td = tr[i].getElementsByTagName("td")[2];
            if (td) {
                txtValue = td.textContent || td.innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }
        }
    }