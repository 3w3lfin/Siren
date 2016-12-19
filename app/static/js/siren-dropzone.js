Dropzone.options.fileupload = {
    acceptedFiles: "image/*",
    maxFiles: 1,
    autoProcessQueue : false,
    init : function() {
        this.on("addedfile", function(file) {
            // Create the remove button
            var removeButton = Dropzone.createElement("<button>Remove</button>");
            // Capture the Dropzone instance as closure.
            var _this = this;
            // Listen to the click event
            removeButton.addEventListener("click", function(e) {
                // Make sure the button click doesn't submit the form:
                e.preventDefault();
                e.stopPropagation();
                // Remove the file preview.
                _this.removeFile(file);

            });
            // Add the button to the file preview element.
            file.previewElement.appendChild(removeButton);
        });
        
        var submitButton = document.querySelector("#submit-all")
        fileupload = this;
        fileupload.on("maxfilesexceeded", function(file) { this.removeFile(file);});
        
        fileupload.on("error", function(file,errorMessage) {
            alert(errorMessage)
            this.removeFile(file)
        });

        submitButton.addEventListener("click", function() {
            fileupload.processQueue();
            // Tell Dropzone to process all queued files.
        });

        this.on("complete", function (file) {
            if (this.getUploadingFiles().length === 0 && this.getQueuedFiles().length === 0) {}
        });
    }
};
