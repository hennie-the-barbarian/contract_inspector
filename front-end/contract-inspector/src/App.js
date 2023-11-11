import './App.css';
import AppTitle from './components/AppTitle';
import ContractToInspect from './components/ContractForm';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <AppTitle/>
        <ContractToInspect/>
      </header>
    </div>
  );
}

export default App;
