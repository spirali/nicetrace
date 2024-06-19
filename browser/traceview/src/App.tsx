import './App.css'
import { TreeView } from './components/TreeView'
import { TracingNode } from './model/Node'

function App(props: { root: TracingNode }) {
  return (
    <div className="container">
      <div className='panel'><TreeView /></div>
      <div className='content'>XXXX</div>
    </div>
  )
}

export default App
