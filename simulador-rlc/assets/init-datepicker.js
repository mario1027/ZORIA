document.addEventListener("DOMContentLoaded", function () {
    const container = document.querySelector('#birthday-container');
    if (container && container.getAttribute('data-init') === 'true') {
        // Genera el campo de entrada dinámicamente
        container.innerHTML = `
            <div class="input-group">
                <input 
                    type="text" 
                    class="form-control" 
                    id="birthday" 
                    placeholder="dd/mm/yyyy" 
                    data-datepicker="true"
                />
            </div>
        `;

        // Inicializa el calendario con vanillajs-datepicker
        const input = container.querySelector('#birthday');
        if (input) {
            new Datepicker(input, {
                autohide: true,
                format: 'dd/mm/yyyy'
            });
        }
    }
});
