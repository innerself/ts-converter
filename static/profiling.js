let currentList = localStorage.getItem('currentList');
currentList = currentList ? JSON.parse(currentList) : [];

let indentation = 4;

const buttonNext = document.getElementById('button-next');
const buttonReset = document.getElementById('button-reset');
const profilingRows = document.getElementById('profiling-rows');

const firstRowText = () => (
    `import time
from loguru import logger
logger.debug('****************************************')
pf_t1 = time.monotonic()`
);

const consequentRowText = (currentLine) => (
    `pf_t${currentLine} = time.monotonic()
logger.debug(f'Time from previous: {pf_t${currentLine} - pf_t${currentLine - 1}}')
logger.debug(f'Time from start: {pf_t${currentLine} - pf_t1}')`
);


async function addRow(rowText, lineNumber) {
    const rowDiv = document.createElement('div');
    const rowLeftWing = document.createElement('div');
    const rowRightWing = document.createElement('div');
    const rowPre = document.createElement('pre');
    const rowCode = document.createElement('code');

    rowDiv.classList.add('row-div', 'invisible');

    rowLeftWing.classList.add('row-left-wing');
    rowDiv.appendChild(rowLeftWing)

    rowPre.classList.add('row-pre');
    rowPre.addEventListener('click', async function () {
        await copyCodeText(this);
        shine(rowPre.parentElement.getElementsByClassName(
            'row-right-wing'
        )[0]);
    });
    rowDiv.appendChild(rowPre);

    rowCode.id = `row-code-${lineNumber}`
    rowCode.textContent = rowText;
    rowCode.classList.add('row-code')
    rowPre.appendChild(rowCode);

    rowDiv.appendChild(rowPre);

    rowRightWing.classList.add('row-right-wing');
    rowRightWing.textContent = '← copied to clipboard'
    rowDiv.appendChild(rowRightWing)

    profilingRows.appendChild(rowDiv);
    rowDiv.scrollIntoView({'behavior': 'smooth'});
    rowDiv.classList.remove('invisible');

    return rowDiv;
}

async function addListElement() {
    const currentLine = currentList.length > 0 ? currentList.length + 1 : 1
    const rowText = currentLine === 1 ? firstRowText() : consequentRowText(currentLine)

    currentList.push(rowText);
    const rowDiv = await addRow(rowText, currentLine);
    await copyCodeText(rowDiv.getElementsByClassName('row-pre')[0])
    shine(rowDiv.getElementsByClassName('row-right-wing')[0])
    localStorage.setItem('currentList', JSON.stringify(currentList));
}

async function resetList() {
    currentList = [];
    await navigator.clipboard.writeText('');
    localStorage.setItem('currentList', JSON.stringify(currentList));
    for (let i = profilingRows.children.length - 1; i >= 0; i--) {
        const child = profilingRows.children[i];
        child.classList.add('invisible');
        const childStyle = window.getComputedStyle(child);
        const transitionDuration = parseFloat(childStyle.transitionDuration) * 1000;
        await new Promise(resolve => setTimeout(resolve, transitionDuration / 2));
        setTimeout(() => {
            profilingRows.removeChild(child);
        }, transitionDuration / 2);
    }
}

async function copyCodeText(preElement) {
    let resultText = preElement.innerText;
    if (indentation > 0) {
        let codeLines = resultText.split('\n');
        codeLines.map(line => ' '.repeat(indentation) + line);
        codeLines.unshift('')
        codeLines.push('')
        resultText = codeLines.join('\n')
    }
    await navigator.clipboard.writeText(resultText);
}

function shine(wing) {
    wing.classList.toggle('shine');
    setTimeout(() => {
        wing.classList.toggle('shine')
    }, 1500)
}

function setButtonNextText(listLength) {
    buttonNext.innerText = listLength === 0 ? 'START' : 'NEXT';
}

async function renderExistingRows() {
    for (let i = 0; i < currentList.length; i++) {
        await addRow(currentList[i], i + 1);
    }
}


setButtonNextText(currentList.length);
renderExistingRows().then(r => null);

buttonNext.addEventListener('click', async function () {
    await addListElement();
    setButtonNextText(currentList.length);
});
buttonReset.addEventListener('click', async function () {
    await resetList();
    setButtonNextText(currentList.length);
});
