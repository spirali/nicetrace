import { TbMessageQuestion } from "react-icons/tb";
import { TracingNode } from "../model/Node";
import { GrTree } from "react-icons/gr";
import { CgShapeCircle } from "react-icons/cg";
import { IoPersonSharp } from "react-icons/io5";
import { IoEyeOutline } from "react-icons/io5";


export function createNodeIcon(node: TracingNode, size?: number) {
    const icon = node.meta?.icon;
    if (icon === "query") {
        return <TbMessageQuestion className="nt-node-icon" size={size} />
    }
    if (icon === "person") {
        return <IoPersonSharp className="nt-node-icon" size={size} />
    }
    if (icon === "eye") {
        return <IoEyeOutline className="nt-node-icon" size={size} />
    }
    if (node.children) {
        return <GrTree className="nt-node-icon" size={size} />
    } else {
        return <CgShapeCircle className="nt-node-icon" size={size} />
    }
}