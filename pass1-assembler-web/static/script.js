document.getElementById('assemblerForm').addEventListener('submit', async (event) => {
    event.preventDefault();  // Prevent the form from submitting the default way (GET)

    // Collect the uploaded files
    const inputFile = document.getElementById('inputFile').files[0];
    const optabFile = document.getElementById('optabFile').files[0];

    // Check if files are selected
    if (!inputFile || !optabFile) {
        alert("Please upload both input.txt and optab.txt");
        return;
    }

    const formData = new FormData();
    formData.append('inputFile', inputFile);
    formData.append('optabFile', optabFile);

    // Send files to the server using fetch API as a POST request
    const response = await fetch('/run_pass1', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();

    // Display the intermediate file and symbol table
    document.getElementById('intermediateFile').textContent = result.intermediateFile;
    document.getElementById('symbolTable').textContent = result.symbolTable;
});
