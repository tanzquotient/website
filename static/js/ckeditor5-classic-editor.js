var {
    ClassicEditor,
    Essentials,
    Bold,
    Italic,
    Font,
    Paragraph,
    Alignment,
    Heading,
    Strikethrough,
    Base64UploadAdapter,
    ImageInsert,
    Image,
    Image,
} = CKEDITOR;

function createEditor(selector) {
    ClassicEditor
        .create(document.querySelector(selector), {
            plugins: [Image, Base64UploadAdapter, ImageInsert, Essentials, Bold, Italic, Strikethrough, Font, Paragraph, Alignment, Heading,],
            toolbar: [
                'undo', 'redo', '|',
                'bold', 'italic', 'strikethrough', '|',
                'alignment', '|',
                'heading', 'fontColor', 'fontBackgroundColor', '|', 'insertImage',
            ],
        })
        .catch(error => {
            console.error(error);
        });
}