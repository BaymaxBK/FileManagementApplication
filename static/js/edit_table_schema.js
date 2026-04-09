//GLOBAL FUNCTIONS 
    function getCookie(name){
            
                let cookieValue = null;
                if ( document.cookie && document.cookie != '' ){
                        let cookies=document.cookie.split(";");
                        for (let cookie of cookies) {
                            cookie = cookie.trim();
                            if (cookie.startsWith(name + "=")) {
                                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                break;
                            }
                        }
                }
                console.log("Cookie value :"+cookieValue)
                return cookieValue; 
            
    }

    // HIDE/SHOW "NO COMPSITE UNIQE CREATED TO THIS TABLE YET" TEXT
    toggleEmptyCompositeText();
    function toggleEmptyCompositeText() {

        
        const container = document.querySelector(".compositeUniques");
        const seleted_items = container.querySelectorAll(".compositeUnqiueSelectedRow"); // each added combo
        const emptyText = container.querySelector(".empty-text");
        if (!container) return; 

        console.log(container," Empty Text Indication <p> tag ",emptyText);
        if (seleted_items.length === 0) {
            emptyText.style.display = "block";
        } else {
            emptyText.style.display = "none";
        }
    }

    
    function sanitizeName(name) {
        return name.trim().toLowerCase().replace(/\s+/g, "_");
    }
    
    // CHECK FIELDS NAME CHANGE BEFORE ADDING COMPOSITE CONTRAINT 
    function hasFieldChanges() {

            let changed = false;
            $("#fields .field-row").each(function () {
            
                const oldName = $(this).find("input[name='old_field_name[]']").val().trim();
                const newName = $(this).find("input[name='field_name[]']").val().trim();
                
                // console.log(`Old Name : '${oldName}' <> New Name '${newName}' <> condition ${sanitizeName(newName) !== oldName}`);
                // compare display vs DB name → careful!
                if (sanitizeName(newName) !== sanitizeName(oldName)) {
                    changed = true;
                    // highlight changed field (optional)
                    $(this).find("input[name='field_name[]']").addClass("border-danger");
                
                    return false; // break loop
                }
            
            });
        
            return changed;
    }

    function isDuplicateCombination(newNames) {

        let isDuplicate = false;
        
        $(".compositeUnqiueSelectedRow").each(function () {
        
            const text = $(this).find("span").text().trim();
            const existing = text.split("+").map(v => v.trim()).sort();
            const incoming = [...newNames].sort();
        
            if (JSON.stringify(existing) === JSON.stringify(incoming)) {
                isDuplicate = true;
                return false;
            }
        
        });
    
        return isDuplicate;
    }
    

     // ADD COMPSITE FIELDS BUTTON
    function addCompositeUnique() {

            if (hasFieldChanges()) {
                alert("⚠️ Please save field changes before adding constraint.");
                return;
            }

            const $checked = $("#compositeUniqueContainer input:checked");
            
            if ($checked.length < 2) {
                alert("Select at least Two field");
                return;
            }
        
            // collect selected values
            const names = [];
            const indexes = [];

            $checked.each(function () {

                indexes.push($(this).data("index"));
                
                const label = $(this).next("label").text().trim();
                names.push(label);

            });

            if (isDuplicateCombination(names)) {
                alert("⚠️ This combination already added");
                return;
            }

            const tableId = $("#tableId").val();
             $.ajax({
                    url: "/add-composite-unique/",
                    type: "POST",
                    contentType: "application/json",
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken")
                    },
                    data: JSON.stringify({
                        table_id: tableId,
                        indexes: indexes,
                        names: names
                    }),

                    success: function (data) {

                        if (data.status === "success") {
                        
                            const $container = $(".compositeUniques");
                        
                            const html = `
                                <div class="d-flex compositeUnqiueSelectedRow justify-content-between align-items-center border rounded px-2 py-1 mb-2"
                                     data-id="${data.id}"
                                     data-constraint="${data.constraint_name}">
                        
                                    <span>${data.display}</span>
                        
                                    <div>
                                        <button type="button" class="btn btn-sm btn-outline-danger delete-composite-btn">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </div>
                                </div>
                            `;
                        
                            $container.append(html);
                        
                            toggleEmptyCompositeText();
                        
                            // uncheck all
                            $checked.prop("checked", false);

                        } else {
                                alert(data.message);
                        }
                    },

                    error: function () {
                        alert("Server error");
                    }
            });



        
            console.log("Added Indice :",indexes);
            const combinationText = values.join(" + ");
        
            // create UI block
            const html = `
                <div class="d-flex compositeUnqiueSelectedRow justify-content-between align-items-center border rounded px-2 py-1 mb-2">
                    <span >${combinationText}</span>
                    
                    <div >
                        <input type="hidden" name="composite_unique_groups[]" value="${indexes.join(",")}">
                        <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeCombination(this)">❌</button>
                    </div>
                </div>
            `;
            
            document.querySelector(".compositeUniques")
                .insertAdjacentHTML("beforeend", html);
            
            // uncheck after adding
            checked.forEach(cb => cb.checked = false);
            toggleEmptyCompositeText();
    }

//FIELD NAME AND UNQUE COMBINERTION SELECT COLUMN SYNC
    function syncCompositeName(input) {
        
        console.log("SyncComposite Name Event Triggered !");
        // console.log("Field Input ",input);
        const index = input.data("index");
        const newValue = input.val();

        console.log("Edited Input value :",newValue,"Index :",index);
        // find matching checkbox block
        const wrapper = document.querySelector(
            `#compositeUniqueContainer [data-index="${index}"]`
        );

        console.log(`Warpper ${wrapper}`);
        if (wrapper) {
            const checkbox = wrapper.querySelector("input");
            const label = wrapper.querySelector("label");

            console.log("checkbox",checkbox);
            // update value + label
            checkbox.value = newValue;
            label.textContent = newValue;
        }
            
        updateCombinationNames(index, newValue);
    }

    $(document).on("click", ".delete-composite-btn", function () {

        if (!confirm("Delete this composite unique constraint?")) return;

        const row = $(this).closest(".compositeUnqiueSelectedRow");

        const constraintId = row.data("id");
        const constraintName = row.data("constraint");

        $.ajax({
            url: "/delete-composite-unique/",
            type: "POST",
            data: {
                id: constraintId,
                constraint_name: constraintName,
                csrfmiddlewaretoken: getCookie("csrftoken")
            },
            success: function (res) {

                if (res.status === "success") {
                    row.remove();
                    toggleEmptyCompositeText();
                } else {
                    alert(res.message);
                }
            },
            error: function () {
                alert("Server error");
            }
        });
    });


    function validateName(input) {
            const errorEl = input.parentElement.querySelector('.form-text');
            const value = input.value.trim();

            // Must start with a-z or underscore, and only contain word chars
            const isValid = /^[a-z_][\w\s]*$/i.test(value);
            
            if (!isValid) {
                errorEl.classList.remove('d-none');
            } else {
                errorEl.classList.add('d-none');
                syncCompositeName(input);
            }
    }


    // UPDATE THE SELECTED UNIQUE COMPIST NAMES
    function updateCombinationNames(index, newValue) {

            console.log("UpdateCombo Triggered !");
            const combos = document.querySelectorAll(
                'input[name="composite_unique_groups[]"]'
            );

            combos.forEach(input => {
                let spited_Indices = input.value.split(",");
                console.log("Splited Values (Indices): ",spited_Indices);

        
                // safer: rebuild from checkbox mapping
                const updated = spited_Indices.map(idx => {
                    // find matching checkbox by value
                    console.log(`Splited Iterativ columnIndex ${idx}`);
                    const cb = document.querySelector(
                        `#compositeUniqueContainer input[data-index="${idx}"]`
                    );

                    console.log("CheckBox Exist ",cb);
                    console.log("Values Need to updated in edited Combo ",idx);
                    return cb ? cb.value : null;

                }).filter(v => v !== null);
            
                console.log("Updated Item ",updated.join(","));
                input.value = spited_Indices.join(",");
            
            
                // update UI text
                const span = input.closest(".compositeUnqiueSelectedRow").querySelector("span");
                span.textContent = updated.join(" + ");

            });
    }



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
                        <input type="hidden" name="old_field_name[]" value="-1">

                        <div class="col-md-4">
                            <input type="text" name="field_name[]" class="form-control" data-index="${index}" value="" placeholder="Field Name" required >
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

            const checkboxId = `comp_${index}`;
            const FieldcheckboxHTML = `
                        <div class="form-check d-flex align-items-center mb-1" data-index="${index}">
                            <input class="form-check-input me-1" type="checkbox" name="composite_unique_fields[]" 
                                  data-index="${index}" id="${checkboxId}" value="">
                            <label class="form-check-label" for="${checkboxId}">
                                Unnamed${index+1}
                            </label>
                        </div>
                    `;

            const addCompositeCombinationBtnHtml =`
            <div id="uniquComboAddWrapper" class="w-100 d-flex justify-content-end mt-2">
                    <button id="comboaddBtn" type="button" class="btn btn-sm btn-primary mt-2" onclick="addCompositeUnique()">
                        + Add 
                    </button>
            </div>`;

            $("#uniquComboAddWrapper").remove();
            $("#compositeUniqueContainer").append(FieldcheckboxHTML);
            $("#compositeUniqueContainer").append(addCompositeCombinationBtnHtml);
            $('#fields').append(fieldHTML);

        });

        $(document).on("click",".constraintToggle-btn", function(){
                                        
                const fieldRow = $(this).closest(".field-row");
                const panel = fieldRow.find(".constraint-row");  // find sibling
                panel.toggle();

            
        });

        // TOGGLE COMPOITE FIELDS DIV
        $(document).on('click','#addConst-id',function(){
            console.log("Add Composite Unique ");
            const modal = new bootstrap.Modal(document.getElementById('compositeModal'));
            modal.show();

        });

        $(document).on('input', 'input[name="field_name[]"]', function () {

            const $input = $(this);
            const value = $input.val().trim();
            const $errorEl = $input.siblings('.form-text');

            const isValid = /^[a-z_][\w\s]*$/i.test(value);

            $errorEl.toggleClass('d-none', isValid);
            if(isValid) syncCompositeName($input);
            
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

        // HIDE/SHOW "NO COMPSITE UNIQE CREATED TO THIS TABLE YET" TEXT
        // function toggleEmptyCompositeText() {
        
        //     const container = document.querySelector(".compositeUniques");
        //     const seleted_items = container.querySelectorAll(".compositeUnqiueSelectedRow"); // each added combo
        //     const emptyText = container.querySelector(".empty-text");
            
        //     console.log("Empty Text Indication <p> tag ",emptyText);
        //     if (seleted_items.length === 0) {
        //         emptyText.style.display = "block";
        //     } else {
        //         emptyText.style.display = "none";
        //     }
        // } 

    

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