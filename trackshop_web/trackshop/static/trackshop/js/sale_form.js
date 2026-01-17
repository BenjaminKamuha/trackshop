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

    function ManageCurrency(){
        const currency = document.getElementById("currency_select").value;
        if (currency === "CDF"){
            var product_price = closestDiv=document.getElementById("product_price");
            var rate = document.getElementById("rate").value;
            var base_price = product_price.value;
            var cdf_price = parseFloat(base_price) * parseFloat(rate);
            product_price.value = cdf_price.toFixed(2);
        } else {
            var product_price = document.getElementById("product_price")
            var rate = document.getElementById("rate").value;
            var cdf_price = product_price.value;
            var base_price = parseFloat(cdf_price) / parseFloat(rate);
            product_price.value = base_price.toFixed(2);
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        updateAddButton();
        updateProductPrice();

    });

    document.getElementById('currency_select').addEventListener('change', function() {

        const currency = document.getElementById('currency_select').value;
        if (currency === 'CDF') {
            document.querySelectorAll(".product-row").forEach(row => {
                var product_price = row.querySelector("input[name='productPrice']").value;
                var qty = row.querySelector("input[name='quantity[]']").value;
                
                // Changement des valeurs
                row.querySelector("input[name='productPrice']").value = (row.querySelector("input[name='productPrice']").value * rate).toFixed(2);
                row.querySelector("input[name='paidAmount[]']").value =(row.querySelector("input[name='paidAmount[]']").value * rate).toFixed(2);
                row.querySelector("input[name='leftOver']").value = ((row.querySelector("input[name='leftOver']").value * rate)).toFixed(2);
                
                row.querySelectorAll("span").forEach(span => {
                    span.textContent = "Fc";
                })
            });
        }
        else{
            document.querySelectorAll(".product-row").forEach(row => {
                var product_price = row.querySelector("input[name='productPrice']").value;
                var qty = row.querySelector("input[name='quantity[]']").value;
                
                // Changement des valeurs
                row.querySelector("input[name='productPrice']").value = (row.querySelector("input[name='productPrice']").value / rate).toFixed(2);
                row.querySelector("input[name='paidAmount[]']").value = (row.querySelector("input[name='paidAmount[]']").value /rate).toFixed(2);
                row.querySelector("input[name='leftOver']").value = ((row.querySelector("input[name='leftOver']").value / rate)).toFixed(2);

                row.querySelectorAll("span").forEach(span => {
                    span.textContent = "$";
                })
            });
        }
    })

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