import { useState, createElement } from "react";
import 'ldrs/bouncy'

function ContractToInspect() {
    const [analysisStarted, setAnalysisStarted] = useState(false)
    const [analysis, setAnalysis] = useState({})
    const [contract, setContract] = useState("")
    const [analysisFinished, setAnlysisFinished] = useState(false)
    
    async function getTaskResult(task) {
        var success = false
        while(!success) {
            console.log(import.meta.env.VITE_APP_API_URL)
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
                break
            }
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

        setContract(formJson.contract)
        const response = await fetch(
            `${import.meta.env.VITE_APP_API_URL}/contracts/analyze/body`, 
            {
                method: 'PUT',
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formJson)
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
            if (analysis.found) {
                return (
                    <div>
                        <h2>Inspection results</h2>
                        <h3>Your contract contains the following problematic clause types</h3>
                        <ul>
                            <li><a href={analysis.link}>{analysis.label}</a></li>
                        </ul>
                        <br />
                        <h3>Instances in document</h3>
                        {highlight_text(contract, analysis.locations)}
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
                <label>
                    Enter contract to inspect:
                    <br />
                    <textarea 
                        name="contract" 
                        rows={12} 
                        cols={100}
                        defaultValue="Enter contract here"
                    />
                </label>
                <br />
                <button type="submit">Inspect Contract</button>
            </form>
        )
    };
}

export default ContractToInspect