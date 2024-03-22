let currentList = localStorage.getItem('currentList');
currentList = currentList ? JSON.parse(currentList) : [];

console.log('')

const buttonNext = document.getElementById('button-next');
const buttonReset = document.getElementById('button-reset');
const profilingRows = document.getElementById('profiling-rows');
const buttonsCopy = document.getElementsByClassName('button-copy');


function addRow(rowText, lineNumber) {
    const rowDiv = document.createElement('div');
    const rowPre = document.createElement('pre');
    const buttonCopy = document.createElement('button');

    rowDiv.classList.add('row-div')

    rowPre.id = `row-pre-${lineNumber}`
    rowPre.textContent = rowText;
    rowPre.classList.add('row-pre')
    rowDiv.appendChild(rowPre);

    buttonCopy.id = `button-copy-${lineNumber}`;
    buttonCopy.textContent = 'COPY'
    buttonCopy.classList.add('button-copy')
    buttonCopy.onclick = async function () {
        await copyPreText(lineNumber);
    }
    rowDiv.appendChild(buttonCopy);

    profilingRows.appendChild(rowDiv);
}

async function addListElement() {
    let currentLine = currentList.length > 0 ? currentList.length + 1 : 1

    let rowText
    if (currentLine === 1) {
        rowText = `
        
        import time
        from loguru import logger
        logger.debug('****************************************')
        pf_t1 = time.monotonic()
        
        `;
    } else {
        rowText = `
        
        pf_t${currentLine} = time.monotonic()
        logger.debug(f'Time from previous: {pf_t${currentLine} - pf_t${currentLine - 1}}')
        logger.debug(f'Time from start: {pf_t${currentLine} - pf_t1}')
        
        `;
    }

    currentList.push(rowText);
    addRow(rowText, currentLine);
    await navigator.clipboard.writeText(rowText);
    localStorage.setItem('currentList', JSON.stringify(currentList));
}

async function resetList() {
    currentList = [];
    await navigator.clipboard.writeText('');
    localStorage.setItem('currentList', JSON.stringify(currentList));
    while (profilingRows.firstChild) {
        profilingRows.removeChild(profilingRows.firstChild);
    }
}

async function copyPreText(lineNumber) {
    const preId = `row-pre-${lineNumber}`;
    const pre = document.getElementById(preId);
    const preText = pre.innerText;
    await navigator.clipboard.writeText(preText);
}


for (let i = 0; i < currentList.length; i++) {
    addRow(currentList[i], i + 1);
}

buttonNext.addEventListener('click', async function() {
    await addListElement();
});
buttonReset.addEventListener('click', async function() {
    await resetList();
});
