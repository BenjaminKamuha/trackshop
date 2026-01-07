document.body.addEventListener('htmx:configRequest', function (e) {
    const btn = e.detail.elt;

    if (btn && btn.id === 'add-product-btn') {
        const selected = Array.from(
            document.querySelectorAll('select[name="product_id[]"]')
        )
        .map(s => s.value)
        .filter(v => v);

        selected.forEach(id => {
            e.detail.parameters['selected_ids[]'] = selected;
        });
    }
});

function updateAddButton() {
    const rows = document.querySelectorAll('.product-row').length;
    const totalProducts = document.querySelectorAll('select[name="product_id[]"] option').length;

    if (rows < totalProducts) {
        document.getElementById('add-product-btn')?.classList.remove('hidden');
    }
    document.getElementById('message_p')?.classList.add('hidden');

}