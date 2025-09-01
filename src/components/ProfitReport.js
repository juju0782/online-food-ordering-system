import React, { useState } from "react";
import axios from "axios";

const ProfitReport = () => {
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");
    const [report, setReport] = useState(null);

    const fetchReport = () => {
        axios.get(`http://127.0.0.1:5000/admin/profit-report?start_date=${startDate}&end_date=${endDate}`)
            .then(response => setReport(response.data))
            .catch(error => console.error("Error fetching report:", error));
    };

    return (
        <div className="p-6">
            <h2 className="text-2xl font-bold mb-4">Profit & Loss Report</h2>
            
            <div className="flex gap-4 mb-4">
                <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="p-2 border rounded"/>
                <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="p-2 border rounded"/>
                <button onClick={fetchReport} className="bg-green-500 text-white p-2 rounded">Get Report</button>
            </div>

            {report && (
                <div className="border p-4 rounded bg-gray-100">
                    <p><strong>Total Revenue:</strong> ${report.total_revenue}</p>
                    <p><strong>Total Cost:</strong> ${report.total_cost}</p>
                    <p><strong>Net Profit:</strong> ${report.total_profit}</p>
                </div>
            )}
        </div>
    );
};

export default ProfitReport;
