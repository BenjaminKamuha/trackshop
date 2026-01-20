    var rate = document.getElementById('rate').value;

    function updateAddButton() {
        const rows = document.querySelectorAll('.product-row').length;
        const totalProducts = document.querySelectorAll('[name="product_id[]"]').length;
        if (rows <= 0){
            document.getElementById('validate-sale-btn')?.classList.add('hidden');
            document.getElementById('help_text')?.classList.remove('hidden');
            document.getElementById('currency')?.classList.add('hidden');
        }
    }

    function updateProductPrice(){
        document.getElementById("quantity").closest('div').classList.add('hidden');
    }


    document.addEventListener('DOMContentLoaded', function() {
        updateAddButton();
        updateProductPrice();

    });

    document.getElementById('currency_select').addEventListener('change', function() {

        const currency = document.getElementById('currency_select').value;
        if (currency === 'CDF') {
            document.querySelectorAll(".product-row").forEach(row => {
                //var product_price = row.querySelector("input[name='productPrice']").value;
                //var qty = row.querySelector("input[name='quantity[]']").value;
                
                // Changement des valeurs
                row.querySelector("input[name='unit_cost[]']").value = (row.querySelector("input[name='unit_cost[]']").value * rate).toFixed(2);
                row.querySelector("input[name='paidAmount[]']").value =(row.querySelector("input[name='paidAmount[]']").value * rate).toFixed(2);
                row.querySelector("input[name='leftOver']").value = ((row.querySelector("input[name='leftOver']").value * rate)).toFixed(2);

                row.querySelectorAll("span").forEach(span => {
                    span.textContent = "Fc";
                })
            });
        }
        else{
            document.querySelectorAll(".product-row").forEach(row => {
                //var product_price = row.querySelector("input[name='productPrice']").value; 
                //var qty = row.querySelector("input[name='quantity[]']").value;
                
                // Changement des valeurs
                row.querySelector("input[name='unit_cost[]']").value = (row.querySelector("input[name='unit_cost[]']").value / rate).toFixed(2);
                row.querySelector("input[name='paidAmount[]']").value = (row.querySelector("input[name='paidAmount[]']").value /rate).toFixed(2);
                row.querySelector("input[name='leftOver']").value = ((row.querySelector("input[name='leftOver']").value / rate)).toFixed(2);

                row.querySelectorAll("span").forEach(span => {
                    span.textContent = "$";
                })
            });
        }
    })

    // Cette écoute nous sert à vérifier la divise de la vente
    document.body.addEventListener("htmx:afterSwap", function (e) {
        // Vérifie que le swap concerne le container des lignes
        const currency = document.getElementById('currency_select').value;
        if (e.target.id === "sale-items") {
            const row = e.target.querySelector(".product-row:last-child");
            if (!row) return;
            // Parcourir UNIQUEMENT les inputs de la nouvelle ligne
            if (currency==="CDF") {
                row.querySelectorAll("input").forEach(input => {
                     // Exemple : focus automatique
                     if (!(input.name == "quantity[]")){
                        input.value = (input.value * rate).toFixed(2) ;
                     }

                     if (input.name == "quantity[]"){
                        input.focus();
                        input.selecte();
                     }
                });

                row.querySelectorAll("span").forEach(span => {
                    span.textContent = "Fc";
                })
            }

            else{
                row.querySelectorAll("span").forEach(span => {
                    span.textContent = "$";
                })
            }
        }
    });