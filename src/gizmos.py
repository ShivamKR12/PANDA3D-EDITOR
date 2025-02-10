from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    CollisionTraverser, CollisionNode, CollisionRay, CollisionHandlerQueue,
    BitMask32, CollisionSphere, Point3, Vec3
)
from direct.task import Task
import math

from direct.showbase.DirectObject import DirectObject
from QPanda3D.Panda3DWorld import Panda3DWorld  # Make sure this returns a proper ShowBase-derived object

class GizmoDemo(DirectObject):
    def __init__(self, world: Panda3DWorld):
        super().__init__()
        
        self.world = world
        self.cam = world.cam
        
        self.move_speed = 1
        
        # Use base.camLens for extruding mouse coordinates.
        self.camLens = self.world.camLens

        # Set up the camera.
        self.world.camera.setPos(10, -20, 10)
        self.world.camera.lookAt(0, 0, 0)
        
        # Create a parent node for the gizmo.
        self.gizmo_root = world.render.attachNewNode("GizmoRoot")
        self.gizmo_root.setPos(0, 0, 0)
        
        # Load gizmo models for the three axes.
        self.gizmo_x = world.loader.loadModel("models/gizmos.obj")
        self.gizmo_x.reparentTo(self.gizmo_root)
        self.gizmo_x.setColor(1, 0, 0, 1)
        self.gizmo_x.setHpr(90, 0, 0)  # Point along +X
        self.gizmo_x.setTag("gizmo", "x")
        
        self.gizmo_y = world.loader.loadModel("models/gizmos.obj")
        self.gizmo_y.reparentTo(self.gizmo_root)
        self.gizmo_y.setColor(0, 1, 0, 1)  # Points along +Y
        self.gizmo_y.setTag("gizmo", "y")
        
        self.gizmo_z = world.loader.loadModel("models/gizmos.obj")
        self.gizmo_z.reparentTo(self.gizmo_root)
        self.gizmo_z.setColor(0, 0, 1, 1)
        self.gizmo_z.setHpr(0, 90, 0)  # Point along +Z
        self.gizmo_z.setTag("gizmo", "z")
        
        self.gizmos = {
            "x": self.gizmo_x,
            "y": self.gizmo_y,
            "z": self.gizmo_z
        }
        
        # --- Collision Setup for Picking ---
        self.pickerMask = BitMask32.bit(10)
        for axis, arrow in self.gizmos.items():
            # Compute tight bounds and create a collision sphere.
            min_bound, max_bound = arrow.getTightBounds()
            center = (min_bound + max_bound) * 0.5
            radius = (max_bound - min_bound).length() * 0.5
            cs = CollisionSphere(center, radius)
            
            
            cnode = CollisionNode('gizmo_' + axis)
            cnode.addSolid(cs)
            cnode.setIntoCollideMask(self.pickerMask)
            arrow.attachNewNode(cnode)
        
        # --- Picking Ray Setup ---
        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue()
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNode.setFromCollideMask(self.pickerMask)
        # Attach the picker node to render so that the ray is global.
        self.pickerNP = world.render.attachNewNode(self.pickerNode)
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP, self.pq)
        
        # --- Dragging State Variables ---
        self.dragAxis = None           # Vec3: the axis along which movement is constrained
        self.initialGizmoPos = None    # Point3: gizmo_root's position at mouse down
        self.initialDragParam = None   # float: parameter along the drag line at mouse down
        
        # Accept mouse events.
        self.accept("mouse1", self.onMouseDown)
        self.accept("mouse1-up", self.onMouseUp)
        self.world.taskMgr.add(self.mouseTask, "mouseTask")
        
        # (Optional) Load an environment for reference.
        self.scene = loader.loadModel("models/environment")
        self.scene.reparentTo(render)
        self.scene.setScale(0.25)
        self.scene.setPos(-8, 42, 0)
        
        # --- Free-Fly Camera Setup ---
        self.camera_speed = 5.0
        self.mouse_sensitivity = 0.1
        self.keys = {
            "w": False,
            "s": False,
            "a": False,
            "d": False,
            "shift": False,
            "space": False
        }
        
        # Bind keys.
        self.accept("w", self.set_key, ["w", True])
        self.accept("w-up", self.set_key, ["w", False])
        self.accept("s", self.set_key, ["s", True])
        self.accept("s-up", self.set_key, ["s", False])
        self.accept("a", self.set_key, ["a", True])
        self.accept("a-up", self.set_key, ["a", False])
        self.accept("d", self.set_key, ["d", True])
        self.accept("d-up", self.set_key, ["d", False])
        self.accept("shift", self.set_key, ["shift", True])
        self.accept("shift-up", self.set_key, ["shift", False])
        self.accept("space", self.set_key, ["space", True])
        self.accept("space-up", self.set_key, ["space", False])
        
        
        # Enable controls
        self.keys = ("w", "s", "q", "e", "a", "d", "mouse2", "arrow_left", "arrow_up", "arrow_down", "arrow_right",
                     "page_up", "page_down")
        self.input = {}
        for i in self.keys:
            self.input[i] = False
            self.accept(i, self.update, extraArgs=[i, True])
            self.accept(i + "-up", self.update, extraArgs=[i, False])

        # Mouse position
        self.accept("mouse-move", self.mouse_move)

        # Camera speed
        # self.accept("wheel_up", self.mouse_up)
        # self.accept("wheel_down", self.mouse_up)

        # Enable movement
        self.move_task = self.add_task(self.move)
        
        # Center the mouse.
        #base.win.movePointer(0, int(base.win.getXSize() / 2), int(base.win.getYSize() / 2))
        print("Initialization complete.")
        
    def mouse_up(self, *args):
        print("uo", args)

    def mouse_move(self, evt: dict):
        self.x, self.y = evt['x'], evt['y']

    def update(self, key, value, *args):
        self.input[key] = value

        # Reseat mouse position
        if args and value:
            args = args[0]
            self.x, self.y = args['x'], args['y']
            self.mx, self.my = self.x, self.y

    def move(self, task):
        # Mouse Rotation
        if self.world.mouseWatcherNode.hasMouse():
            if self.input["mouse2"]:
                dx, dy = self.mx - self.x, self.my - self.y

                self.cam.set_p(self.cam, dy * 0.25 * self.move_speed)
                self.cam.set_h(self.cam, dx * 0.25 * self.move_speed)

                self.mx, self.my = self.x, self.y

        # Keyboad Movement
        if self.input["q"] or self.input["page_up"]:
            self.cam.set_z(self.cam, 1 * self.move_speed)

        if self.input["e"] or self.input["page_down"]:
            self.cam.set_z(self.cam, -1 * self.move_speed)

        if self.input["w"] or self.input["arrow_up"]:
            self.cam.set_y(self.cam, 1 * self.move_speed)

        if self.input["s"] or self.input["arrow_down"]:
            self.cam.set_y(self.cam, -1 * self.move_speed)

        if self.input["d"] or self.input["arrow_right"]:
            self.cam.set_x(self.cam, 1 * self.move_speed)

        if self.input["a"] or self.input["arrow_left"]:
            self.cam.set_x(self.cam, -1 * self.move_speed)

        return task.cont
    
    def set_key(self, key, value):
        self.keys[key] = value
    
    def computeDragParameter(self, r0, rdir, linePoint, lineDir):
        """
        Given a ray (r0, rdir) and a line (linePoint, lineDir),
        compute the parameter t along the line for the closest point to the ray.
        """
        d = lineDir.normalized()
        w0 = linePoint - r0
        B = d.dot(rdir)
        denom = 1 - B * B
        if math.fabs(denom) < 1e-5:
            return 0.0
        t = (-d.dot(w0) + B * rdir.dot(w0)) / denom
        return t
    
    def onMouseDown(self, position):
        if not base.mouseWatcherNode.hasMouse():
            return
        
        
        mpos = position
        nearPoint = Point3()
        farPoint = Point3()
        pMouse = base.mouseWatcherNode.getMouse()
        base.camLens.extrude(pMouse, nearPoint, farPoint)
        r0 = render.getRelativePoint(self.world.camera, nearPoint)
        rFar = render.getRelativePoint(self.world.camera, farPoint)
        rdir = (rFar - r0).normalized()
        self.pickerRay.setOrigin(r0)
        self.pickerRay.setDirection(rdir)
        
        self.picker.traverse(self.gizmo_root)
        
        if self.pq.getNumEntries() > 0:

            self.pq.sortEntries()
            entry = self.pq.getEntry(0)
            pickedObj = self.pq.getEntry(0).getIntoNodePath()
            pickedObj = pickedObj.findNetTag('gizmo')
            if not pickedObj.isEmpty():
                nodeName = entry.getIntoNode().getName()  # e.g., "gizmo_x"
                if nodeName.startswith("gizmo_"):
                    print("Picked gizmo:", nodeName)
                    axis = nodeName.split("_")[-1]
                    if axis == "x":
                        self.dragAxis = Vec3(1, 0, 0)
                    elif axis == "y":
                        self.dragAxis = Vec3(0, 1, 0)
                    elif axis == "z":
                        self.dragAxis = Vec3(0, 0, 1)
                    else:
                        self.dragAxis = None

                    if self.dragAxis is not None:
                        self.initialGizmoPos = self.gizmo_root.getPos(self.world.render)
                        linePoint = self.initialGizmoPos
                        lineDir = self.dragAxis
                        self.initialDragParam = self.computeDragParameter(r0, rdir, linePoint, lineDir)
                        print("Dragging axis:", axis, "initial param =", self.initialDragParam)
    
    def onMouseUp(self, position):
        self.dragAxis = None
        self.initialGizmoPos = None
        self.initialDragParam = None
    
    def mouseTask(self, task):
        if self.dragAxis is not None and self.initialDragParam is not None and base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            nearPoint = Point3()
            farPoint = Point3()
            base.camLens.extrude(mpos, nearPoint, farPoint)
            r0 = render.getRelativePoint(self.world.camera, nearPoint)
            rFar = render.getRelativePoint(self.world.camera, farPoint)
            rdir = (rFar - r0).normalized()
            
            linePoint = self.initialGizmoPos
            lineDir = self.dragAxis
            currentParam = self.computeDragParameter(r0, rdir, linePoint, lineDir)
            deltaParam = currentParam - self.initialDragParam
            newPos = self.initialGizmoPos + self.dragAxis * deltaParam
            self.gizmo_root.setPos(render, newPos)
            # Debug: print updated position.
            # print("New gizmo pos:", newPos)
        return Task.cont

if __name__ == "__main__":
    # Create a Panda3DWorld instance (make sure your Panda3DWorld class sets up ShowBase properly).
    world = Panda3DWorld()
    demo = GizmoDemo(world)
    demo.run()
