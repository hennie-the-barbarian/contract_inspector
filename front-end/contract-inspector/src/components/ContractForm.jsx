import { useState, createElement } from "react";
import 'ldrs/bouncy';

function ConcernsFound({label, concerns}) {
    console.log("Concerns: ")
    console.log(concerns)
    const listItems = concerns.map(
        concern => 
            <li>
                <h4>{concern.concern_name}</h4>
                {concern.description}
                <br />
                <br />
                Additional info
                <br />
                {concern.more_info}
                <br />
            </li>
    )
    console.log(listItems)
    return (
        <div>
            <h3>{label}</h3>
            <ul>
                {listItems}
            </ul>
        </div>
    )
}

function ContractToInspect() {
    const [analysisStarted, setAnalysisStarted] = useState(false)
    const [analysis, setAnalysis] = useState({})
    const [contract, setContract] = useState("")
    const [analysisFinished, setAnlysisFinished] = useState(false)
    const municipalities = [
        { value: 'minneapolis', label: 'Minneapolis, MN' }
    ]
    const contract_types = [
        { value: 'rental_agreement', label: 'Rental Agreement' }
    ]
    
    async function getTaskResult(task) {
        var success = false
        let sleep_length = 1000
        while(!success && sleep_length < 120000) {
            console.log(`current sleep length: ${sleep_length}`)
            const response = await fetch(
                `${import.meta.env.VITE_APP_API_URL}/contracts/analyze/body/job/${task}`, 
                {
                    method: 'GET'
                }
            );
            let analysisResponse = await response.json()
            if (analysisResponse.status !== 'PENDING') {
                setAnlysisFinished(true)
                setAnalysis(analysisResponse.result)
                console.log(analysisResponse)
                console.log(analysisResponse.result)
                console.log(analysis)
                success = true
            }
            await new Promise(r => setTimeout(r, sleep_length));
            sleep_length = sleep_length * 2
        }
    }

    async function handleSubmit(e) {
        // Prevent the browser from reloading the page
        e.preventDefault();
        // Read the form data
        setAnalysisStarted(true)
        const form = e.target;
        const formData = new FormData(form);
        // Or you can work with it as a plain object:
        const formJson = Object.fromEntries(formData.entries());
        console.log(formJson)
        setContract(formJson.contract)
        const fileUpload = new FormData();
        fileUpload.append("file", formData.get('contract_file'));
        console.log(`${import.meta.env.VITE_APP_API_URL}/contracts/analyze/file/${formJson.contract_type}`)
        let response = await fetch(
            `${import.meta.env.VITE_APP_API_URL}/contracts/analyze/file/${formJson.contract_type}`, 
            {
                method: 'PUT',
                body: fileUpload
            }
        );
        let analysisResponse = await response.json()

        setAnalysisStarted(true)
        getTaskResult(analysisResponse.task_id)
    }

    function highlight_text(text, highlight_ranges) {
        let highlighted_text = []
        let previous_index = 0
        for (const highlight_range of highlight_ranges) {
            for (const highlight of highlight_range) {
                highlighted_text = highlighted_text.concat(
                    text.substring(previous_index, highlight[0]),
                    createElement(
                        'b',
                        {style: {'backgroundColor':'blue'}},
                        text.substring(highlight[0], highlight[1])
                    )
                )
                previous_index = highlight[1]
            }
        }
        if (previous_index < text.length) {
            highlighted_text = highlighted_text.concat(
                text.substring(previous_index)
            )
        }
        return highlighted_text
    }

    if (analysisStarted) {
        if (analysisFinished) {
            if (analysis.issues_found) {
                return (
                    <div>
                        <h2>Inspection results</h2>
                        {   analysis.illegal_issues.length > 0  &&
                            <ConcernsFound label='Potentially Illegal Clauses'
                                           concerns={analysis.illegal_issues} />
                        }
                        {   analysis.warning_issues.length > 0  &&
                            <ConcernsFound label='Concerning Clauses'
                                           concerns={analysis.warning_issues} />
                        }
                        {   analysis.info_issues.length > 0  &&
                            <ConcernsFound label='Useful Information'
                                           concerns={analysis.info_issues} />
                        }
                    </div>
                )
            }
            else {
                return (
                    <div>
                        No obvious concerns. This doesn't mean you shouldn't be careful,
                        just that contract inspector couldn't find anything problematic.
                    </div>
                )
            }
        }
        else {
            return(
                <div>
                    We've got our best robots inspecting your contract. Results incoming.
                    <br />
                    <br />
                    <l-bouncy size="100" color="coral"></l-bouncy>
                </div>
            )
        }
    }
    else {
        return(
            <form method="post" onSubmit={handleSubmit}>
                <br />
                Type of contract
                <br />
                <select name="contract_type" id="contract_type">
                    <option value="rental-agreement">Rental Agreement</option>
                </select>
                <br />
                <br />
                Contract to inspect
                <br />
                <div>
                    <input name="contract_file" type="file" />
                </div>
                <br />
                <button type="submit">Inspect Contract</button>
            </form>
        )
    };
}

export default ContractToInspect