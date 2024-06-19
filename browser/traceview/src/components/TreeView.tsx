import "./TreeView.css"


export function TreeView() {
    return (<div className="tree">
        <ul>
            <li>
                Fruit
                <ul>
                    <li>
                        Red
                        <ul>
                            <li>Cherry</li>
                            <li>Strawberry</li>
                        </ul>
                    </li>
                    <li>
                        Yellow
                        <ul>
                            <li>Banana</li>
                        </ul>
                    </li>
                </ul>
            </li>
            <li>
                Meat
                <ul>
                    <li>Beef</li>
                    <li>Pork</li>
                </ul>
            </li>
        </ul>
    </div>);
}