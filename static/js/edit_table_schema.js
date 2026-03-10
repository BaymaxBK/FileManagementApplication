$(function () {
        
        let fieldIndex = $('.field-row').length;
        console.log("Fields Length ",fieldIndex);

        function getCSRFToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]').value;
        }

        $('.field_type, .maxLengthField').on(
            'mousedown keydown wheel touchstart',
            
            function (e) {
                console.log('Event triggered:', e.type, this);
                e.preventDefault();
            }
        );
        
        // ADD COLUMN BUTTON EVENT
        $('#addField-id').on("click",function(){

                const index = fieldIndex++;
                const fieldHTML =`<div class="row g-2 mb-2 mt-1 field-row">
                        
                        <input type="hidden" name="old_field_id[]" value="-1">
                        <div class="col-md-4">
                            <input type="text" name="field_name[]" class="form-control" placeholder="Field Name" required >
                            <div class="form-text text-danger d-none py-2">❌ Invalid field name.</div>
                        </div>

                        <div class="col-md-4">
                            <select name="field_type[]" class="form-select field_type" required>
                                <option value="">Select Field Type</option>
                                <option value="VARCHAR(255)">Text</option>
                                <option value="INTEGER">Number</option>
                                <option value="DATE">Date</option>
                                <option value="BOOLEAN">Boolean</option>
                            </select>
                        </div>
                        
                
                        <div class="col-md-2 maxLengthField-div" style="display:none;">
                            <input type="text" name="max_length[]"  class="form-control maxLengthField" placeholder="Max Size" value="255" ></intput>
                        </div>
                        
                        <div class="col-md-2">                            
                            <button  type="button" class="btn btn-outline-danger btn-sm remove-Field-row" ><i class="bi bi-trash"></i></button>
                            <button type="button" class="btn btn-outline-secondary btn-sm constraintToggle-btn" >⚙️</button>
                        </div>

                    

                    <div class="flex-center mb-2 flex-warp gap-1 constraint-row" style="display: none;">

                            <div class="w-50 d-flex justify-content-start border rounded">
                                <label class="form-label flex-center px-1"><input class="mx-1" type="checkbox" style="width:1rem; height:1rem;" name="not_null[${index}]" value="1"> NOT NULL</label>
                            </div>
                            
                            <div class="w-50 d-flex justify-content-start border rounded">
                                <label class="form-label flex-center px-1"><input class="mx-1" type="checkbox" name="unique[${index}]" style="width:1rem; height:1rem;" value="1"> UNIQUE</label>
                            </div>
                            
                            <div class="w-50 flex-center">
                                <label class="form-label px-2">Default:</label> <input type="text" name="default_value[]" placeholder="(optional)" class="form-control">
                            </div>
                            
                            <div class="w-50 flex-center">
                                <label class="form-label px-2">Check:</label> <input type="text" name="check_condition[]" placeholder="e.g. age >= 18" class="form-control">
                            </div>
                            
                             <div class="w-50 d-flex justify-content-start border rounded">
                                <label class="form-label flex-center px-1"><input class="mx-1" type="checkbox" name="composite_unique[]" style="width:1rem; height:1rem;" value="0"> Composite Unique</label>
                            </div>

                        </div>

                    </div>`;

            $('#fields').append(fieldHTML);

        });

        $(document).on("click",".constraintToggle-btn", function(){
                                        
                const fieldRow = $(this).closest(".field-row");
                const panel = fieldRow.find(".constraint-row");  // find sibling
                panel.toggle();

            
        });

        $(document).on('input', 'input[name="field_name[]"]', function () {

            const $input = $(this);
            const value = $input.val().trim();
            const $errorEl = $input.siblings('.form-text');

            const isValid = /^[a-z_][\w\s]*$/i.test(value);

            $errorEl.toggleClass('d-none', isValid);
        });

        
        $(document).on('input', 'input[name="max_length[]"]', function () {
                
                const $input = $(this);
                let value = $input.val().replace(/[^0-9]/g, '');
                value = value.replace(/^0+/, '');
                $input.val(value); 
        });
        
        //REMOVE FILED ROW BUTTON 
        $(document).on('click', '.remove-Field-row', function () {

                console.log("Delete button Clicked !");
                const fieldRow = $(this).closest('.field-row');
                const fieldId = fieldRow.find('input[name="old_field_id[]"]').val();
                
                console.log("Delete Filed rowId > :", fieldId);
                
                if (fieldId === "-1") {
                    fieldRow.remove();
                    return                    
                }
                if (!confirm(" Delete this column permanently ?")) return;

                $.ajax({
                    url:`/custom_table/delete-field/${fieldId}`,
                    type:"POST",
                    headers: {
                        "X-CSRFToken": getCSRFToken()
                    },
                    success: function (res) {
                        if (res.success) fieldRow.remove();
                        else alert(res.error);
                    },
                    
                })
        });


        $(document).on('change', '.field_type', function () {
               const $select = $(this);
               const $fieldRow = $select.closest('.field-row');
               const $maxLengthDiv = $fieldRow.find('.maxLengthField-div');
               
               const selectedValue = $select.val();

                if (selectedValue && selectedValue.includes('VARCHAR')) {
                    $maxLengthDiv.show();   // or .css('display', 'block')
                } else {
                    $maxLengthDiv.hide();
                }
               
            
        });

        // document.addEventListener("change", function(event) {
            
        //     if(event.target.classList.contains("field_type")){
                
        //         const field_row=event.target.closest(".field-row");
        //         const maxLengthField_div = field_row.querySelector(".maxLengthField-div");
        //         const maxLen_input=field_row.querySelector(".maxLengthField");
                
        //         console.log("MaxInput : ",maxLen_input,"this value :",event.target.value)
        //         if (event.target.value == "VARCHAR(255)") {
        //             maxLengthField_div.style.display = "block";
        //             maxLen_input.required = true;
        //         } else {
        //             maxLengthField_div.style.display = "none";
        //             maxLen_input.required = false;
        //         }
        //     }

        // });

});