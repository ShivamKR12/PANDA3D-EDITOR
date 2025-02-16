from panda3d.core import (
    ShaderTerrainMesh, Shader, MouseWatcher, Point3,
    NodePath, CollisionRay, CollisionNode, CollisionHandlerQueue, CollisionTraverser,
    PNMImage, Filename, LVecBase4f, PNMPainter, PNMBrush, SamplerState, CollisionBox, BitMask32,
    Geom, GeomNode, GeomVertexFormat, GeomVertexData, GeomVertexWriter, GeomLines, Texture, LColorf,
    CardMaker, TransparencyAttrib
)

from panda3d.bullet import BulletDebugNode

from direct.showbase.ShowBase import ShowBase
from panda3d.core import load_prc_file_data

from PIL import Image
from PIL import ImageEnhance

# Initialize Panda3D app
load_prc_file_data('', '')

from direct.showbase.DirectObject import DirectObject
from QPanda3D.Panda3DWorld import Panda3DWorld


from panda3d.core import (
    NodePath, PNMImage, Filename, BitMask32
)
from panda3d.bullet import (
    BulletWorld, BulletRigidBodyNode, BulletHeightfieldShape, ZUp
)

class TerrainCollider:
    def __init__(self, terrain_size, subdivisions, terrain):
        self.terrain_size = terrain_size
        self.subdivisions = subdivisions

        # Create a root node for collision objects.
        self.root = NodePath("TerrainColliders")
        self.root.reparentTo(render)  # Use reparentTo (capital T)

        # Optionally, create additional colliders (if needed).
        self.create_collider_tree()
        
        # Initialize Bullet Physics World.
        self.bullet_world = BulletWorld()
        self.bullet_world.setGravity((0, 0, -9.81))
        
        self.terrain = terrain

        # Load the initial heightmap.
        self.heightmap = PNMImage()
        # Check if terrain.heightmap_image is a string or a PNMImage.
        if isinstance(terrain.heightmap_image, str):
            # If it is a filename, load from file.
            if not self.heightmap.read(Filename(terrain.heightmap_image)):
                print("❌ Failed to load heightmap")
                return
        elif isinstance(terrain.heightmap_image, PNMImage):
            # Otherwise, copy the provided PNMImage.
            self.heightmap = terrain.heightmap_image
        else:
            print("❌ Unrecognized type for heightmap_image")
            return

        print("✅ Heightmap loaded successfully")

        # Create the Bullet Heightfield Shape.
        self.max_height = 10.0  # Maximum height scale.
        self.terrain_shape = BulletHeightfieldShape(self.heightmap, self.max_height, ZUp)
        
        # Create the Bullet rigid body node for the terrain.
        self.terrain_node = BulletRigidBodyNode('Terrain')
        
        
        self.terrain_node.addShape(self.terrain_shape)
        self.terrain_node.setMass(0)  # Static terrain.
        
        # Attach the terrain collision node to the scene.
        self.terrain_np = render.attachNewNode(self.terrain_node)
        self.terrain_np.setPos(0, 0, 0)
        
        # Set a collision mask so that picking (or other systems) detect it.
        self.terrain_np.node().setIntoCollideMask(BitMask32.bit(1))

        # Add the terrain rigid body to the Bullet world.
        self.bullet_world.attachRigidBody(self.terrain_node)

    def create_collider_tree(self):
        """
        Optionally, create a tree of collision boxes that subdivide the terrain.
        The following is an example that is commented out. Uncomment and modify
        if you want to use subdivided collision boxes instead of (or in addition to)
        the Bullet heightfield shape.
        """
        """
        from panda3d.core import CollisionNode, CollisionBox, Point3
        size = self.terrain_size
        step = size / self.subdivisions  # Size of each subdivision.
        half_size = step / 2.0
        for x in range(self.subdivisions):
            for y in range(self.subdivisions):
                # Calculate the center for each subdivision.
                center_x = (x * step) + half_size
                center_y = (y * step) + half_size
                center_z = 5  # Adjust center height as needed.
                collider_node = CollisionNode(f"Collider_{x}_{y}")
                # Create a collision box; dimensions: half extents along x, y, and z.
                collider_box = CollisionBox(Point3(center_x, center_y, center_z), half_size, half_size, 5)
                collider_node.addSolid(collider_box)
                collider_node.setFromCollideMask(BitMask32.bit(1))
                collider_node.setIntoCollideMask(BitMask32.bit(1))
                collider_np = self.root.attachNewNode(collider_node)
        """
        pass  # Currently, we do nothing here.

    def update_colliders(self, updated_area):
        """
        Update the terrain collision shape in-place without creating a new BulletRigidBodyNode.
        The 'updated_area' parameter can be used to indicate which portion was changed.
        """
        print(f"Updating colliders in area: {updated_area}")

        # Create a new heightfield shape from the updated heightmap.
        new_shape = BulletHeightfieldShape(self.heightmap, self.max_height, ZUp)

        # Remove all existing shapes from the rigid body.
        # (Assuming BulletRigidBodyNode supports removeShape or a similar method.)
        num_shapes = self.terrain_node.getNumShapes()
        for _ in range(num_shapes):
            # Always remove the first shape (index 0) until none remain.
            self.terrain_node.removeShape(self.terrain_node.getShape(0))

        # Add the updated shape.
        self.terrain_node.addShape(new_shape)

        # (Optional) Reapply the collision mask if needed.
        #self.terrain_node.setIntoCollideMask(BitMask32.bit(1))
        self.terrain_node.setIntoCollideMask(BitMask32.bit(0))

class TerrainPainterApp(DirectObject):
    def __init__(self, world: Panda3DWorld, panda_widget):
        super().__init__()
        self.world = world
        self.widget = panda_widget
        self.holding = False
        
        # Collision update throttling variables:
        self.collision_update_interval = 1.0  # Increase interval to reduce frequency
        self.last_collision_update_time = 0.0
        self.collision_update_needed = False
        self.updated_area = None

        # Brush properties
        self.brush_size = 100
        self.brush_intensity = 1.0
        self.terrain_height = 1.0

        # Add a task to handle collision updates
        #self.world.add_task(self.update_collision_task, "update_collision_task")

        # Create the brush visual

        # Add a task to update the brush visual
        #self.world.add_task(self.update_brush_visual_task, "update_brush_visual_task")


        

        # Load the heightmap image as a PNMImage
        self.heightmap_image = PNMImage(Filename("./images/Heightmap.png"))

        self.heightmap_image = PNMImage(512, 512)  # Resize to 512x512

        # Create a texture for the heightmap and load the PNMImage into it
        self.heightmap_texture = Texture()
        self.heightmap_texture.load(self.heightmap_image)

        self.terrain_node = ShaderTerrainMesh()
        self.terrain_node.heightfield = base.loader.loadTexture("./images/Heightmap.png")
        self.terrain_node.target_triangle_width = 10.0
        self.terrain_node.generate()

        self.terrain_np = base.render.attach_new_node(self.terrain_node)
        self.terrain_np.set_scale(512, 512, 100)
        self.terrain_np.set_pos(-512 // 2, -512 // 2, -70.0)


        grass_tex = base.loader.loadTexture("./images/Grass.png")
        grass_tex.set_minfilter(SamplerState.FT_linear_mipmap_linear)
        grass_tex.set_anisotropic_degree(16)
        self.terrain_np.set_texture(grass_tex)

        self.collision_traverser = CollisionTraverser()
        self.collision_handler = CollisionHandlerQueue()

        # Load and set the terrain shader with the USE_BRUSH preprocessor directive
        terrain_shader = Shader.load(Shader.SL_GLSL, "terrain.vert.glsl", "terrain.frag.glsl")
        self.terrain_np.set_shader_input("USE_BRUSH", True)
        self.terrain_np.set_shader_input("brush_pos", LVecBase4f(0, 0, 0, 0))
        self.terrain_np.set_shader_input("brush_size", self.brush_size)

        self.terrain_np.set_shader(terrain_shader)
        self.terrain_np.set_shader_input("camera", base.camera)
        
        base.accept("f3", base.toggleWireframe)

        self.mouse_ray = CollisionRay()
        self.mouse_node = CollisionNode('./images/mouse_ray')
        self.mouse_node.add_solid(self.mouse_ray)
        self.mouse_node.set_from_collide_mask(BitMask32.bit(10))
        self.mouse_node.set_into_collide_mask(BitMask32.bit(10))
        self.mouse_node_path = base.camera.attach_new_node(self.mouse_node)

        self.collision_traverser.add_collider(self.mouse_node_path, self.collision_handler)

        #self.terrain_np.set_collide_mask(BitMask32.bit(1))

        # Define collision masks for different categories.
        self.gizmo_mask = BitMask32.bit(10)
        self.terrain_mask = BitMask32.bit(2)
        self.object_mask = BitMask32.bit(3)
        self.ui_mask = BitMask32.bit(4)
        combimed_mask = self.gizmo_mask | self.terrain_mask | self.object_mask | self.ui_mask

        self.accept('mouse1', self.start_holding)
        self.accept('mouse1-up', self.stop_holding)
        self.accept("mouse-move", self.mouse_move)
        self.mx, self.my = 0,0

        self.terrain_collider = TerrainCollider(1024, 100, self)

        self.brush_selection = "./images/b0.png"  #current brush Path

        self.intensity = 0.2  # out of a 100 2/100

        self.max_height = 1
        
        self.create_brush_visual()

        # Enable Bullet debug rendering
        self.enable_bullet_debug()

    def create_brush_visual(self):
        
        # Create a circular texture for the brush visual
        circle_tex = PNMImage(256, 256, 4)
        circle_tex.fill(0, 0, 0)  # Fill with transparent black

        center_x = circle_tex.get_x_size() // 2
        center_y = circle_tex.get_y_size() // 2
        radius = min(center_x, center_y)

        # Embed the brush visual into the terrain shader
        self.terrain_np.set_shader_input("brush_pos", LVecBase4f(0, 0, 0, 0))
        self.terrain_np.set_shader_input("brush_size", self.brush_size)

    def update_brush_visual(self, hit_pos):
        if hit_pos:
            self.terrain_np.set_shader_input("brush_pos", LVecBase4f(hit_pos.x, hit_pos.y, hit_pos.z, 1))
        else:
            self.brush_visual.hide()
            self.terrain_np.set_shader_input("brush_pos", LVecBase4f(0, 0, 0, 0))
        self.terrain_np.set_shader_input("brush_size", self.brush_size)

    def update_brush_visual_task(self, task):
        if self.world.mouseWatcherNode.has_mouse():
            return task.cont
        mouse_pos = self.world.mouseWatcherNode.getMouse()
        pFrom = Point3()
        pTo = Point3()
        self.world.camLens.extrude(mouse_pos, pFrom, pTo)
        pFrom = self.world.render.get_relative_point(self.world.cam, pFrom)
        pTo = self.world.render.get_relative_point(self.world.cam, pTo)
        
        result = self.terrain_collider.bullet_world.rayTestClosest(pFrom, pTo)
        if result.hasHit():
            hit_pos = result.getHitPos()
            self.update_brush_visual(hit_pos)
        else:
            self.update_brush_visual(None)
        return task.cont

    def start_holding(self, position):
        self.mx, self.my = position['x'], position['y']
        self.world.add_task(self.on_mouse_click, "on_mouse_click", appendTask=True)
        self.height = 0.0
        self.holding = True

    def stop_holding(self, position):
        self.holding = False

    def mouse_move(self, evt: dict):
        self.mx, self.my = evt['x'], evt['y']
        

    def adjust_speed_of_brush(self, brush_image, speed_factor):
        # Create a new PNMImage with the same size and data as the original
        new_brush_image = PNMImage(brush_image.get_x_size(), brush_image.get_y_size())
        new_brush_image.copy_sub_image(brush_image, 0, 0, 0, 0, brush_image.get_x_size(), brush_image.get_y_size())

        # Modify pixel values based on speed_factor
        for x in range(new_brush_image.get_x_size()):
            for y in range(new_brush_image.get_y_size()):
                # Get the pixel value at (x, y)
                r, g, b = new_brush_image.get_xel(x, y)

                # Adjust pixel intensity based on speed_factor
                r = int(r * speed_factor)
                g = int(g * speed_factor)
                b = int(b * speed_factor)

                # Ensure pixel values stay within the valid range (0-255)
                r = min(max(r, 0), 255)
                g = min(max(g, 0), 255)
                b = min(max(b, 0), 255)

                # Set the new pixel value
                new_brush_image.set_xel(x, y, r, g, b)

        return new_brush_image

    def highlight_object(self, object_entry):
        object_n = object_entry.get_into_node_path()
        object_n.set_color(1, 0, 0, 1)
        print(f"Object highlighted: {object_n.get_name()}")

    def on_mouse_click(self, Task):
        # Ensure mouse is within bounds
        if not base.mouseWatcherNode.hasMouse():
            print("Mouse not detected.")
            return Task.cont
    
        pMouse = self.world.mouseWatcherNode.getMouse()
        #pMouse = self.mx, self.my
        pFrom = Point3()
        pTo = Point3()
        base.camLens.extrude(pMouse, pFrom, pTo)
        pFrom = render.getRelativePoint(base.cam, pFrom)
        pTo = render.getRelativePoint(base.cam, pTo)
        
        # let's not...
        # Use Bullet's rayTestClosest to test against the Bullet world.
        result = self.terrain_collider.bullet_world.rayTestClosest(pFrom, pTo)
        self.terrain_collider.update_colliders(None)
        
        # update ray's origin and direction
        self.mouse_ray.set_origin(pFrom)
        self.mouse_ray.set_direction((pTo - pFrom).normalized())
        # traverse the scene graph
        self.collision_handler.clear_entries()
        self.collision_traverser.traverse(render)



        # Check for collisions
        if result.hasHit():
            hit_pos = result.getHitPos()
            print("Bullet collision detected at:", hit_pos)
            #self.paint_on_terrain(hit_pos)
        else:
            print("No collision detected.")

        if self.collision_handler.get_num_entries() > 0:
            print("Click detected!")
            self.collision_handler.sort_entries()
            entries = self.collision_handler.get_entries()

            # Filter entries based on collision masks.
            gizmo_entries = [e for e in entries if e.get_into_node_path().get_collide_mask() & self.gizmo_mask]
            if gizmo_entries:
                gizmo_entry = gizmo_entries[0]
                print("Clicked on gizmos")
                self.base.animator_tab.start_gizmo_drag(gizmo_entry)
                return Task.done
            terrain_entries = [e for e in entries if e.get_into_node_path().get_collide_mask() & self.terrain_mask]
            if terrain_entries:
                terrain_entry = terrain_entries[0]
                print("Clicked on terrain")
                # Handle terrain collision...
                return Task.done
            object_entries = [e for e in entries if e.get_into_node_path().get_collide_mask() & self.object_mask]
            if object_entries:
                object_entry = object_entries[0]
                print("Click on a object")
                # Handle object selection
                self.selected_object = object_entry.get_into_node_path()
                self.highlight_object(object_entry)
                return Task.done
            ui_entries = [e for e in entries if e.get_into_node_path().get_collide_mask() & self.ui_mask]
            if ui_entries:
                ui_entry = ui_entries[0]
                print("Clicked on UI")
                # Handle UI interaction...
                return Task.done
    
        if not self.height >= self.max_height:
            self.height += 0.02
    
        #return Task.cont if self.holding else Task.done



    def adjust_brightness_pillow(self, brush_image_path, brightness_factor):
        from PIL import Image
        # Open the brush image and ensure it has an alpha channel.
        brush_image = Image.open(brush_image_path).convert('RGBA')
        
        # Split into individual channels.
        r, g, b, a = brush_image.split()
        
        # Adjust the alpha channel.
        # brightness_factor here is treated as an opacity multiplier.
        # For example, a brightness_factor of 0.5 will make the image 50% as opaque.
        a = a.point(lambda i: int(i * brightness_factor))
        
        # Merge channels back together.
        brush_image = Image.merge('RGBA', (r, g, b, a))
        
        # Save the modified image temporarily.
        brush_image.save("./images/Temp_Brush.png")
        
        # Convert it back to a PNMImage.
        pnm_brush_image = PNMImage(Filename("./images/Temp_Brush.png"))
        return pnm_brush_image
    
    def update_brush_size(self, size):
        
        self.brush_size = size
        
    def update_brush_intensity(self, intesity):
        
        self.brush_intesity = intesity
        
    def update_terrain_height(self, terrain_height):
        
        self.terrain_np.set_scale_z(terrain_height)
        
    

    def paint_on_terrain(self, hit_pos):
        # Map world position to heightmap coordinates.
        terrain_x = int((hit_pos.x + 256) / 512 * self.heightmap_image.get_x_size())
        terrain_y = int((hit_pos.y + 256) / 512 * self.heightmap_image.get_y_size())

        # Flip the Y-axis if necessary.
        terrain_y = self.heightmap_image.get_y_size() - terrain_y - 1

        if 0 <= terrain_x < self.heightmap_image.get_x_size() and 0 <= terrain_y < self.heightmap_image.get_y_size():
            print(f"Painting at heightmap coords: ({terrain_x}, {terrain_y})")

            # (Optional) Adjust brightness of the brush image.
            self.adjust_brightness_pillow(self.brush_selection, self.height)

            # Load the brush image.
            brush_image = PNMImage(Filename("./images/Temp_Brush.png"))
            brush_width = brush_image.get_x_size()
            brush_height = brush_image.get_y_size()

            # (Optional) Adjust the brush speed/intensity.
            self.adjust_speed_of_brush(brush_image, self.intensity)

            # Calculate the top-left corner to center the brush.
            start_x = terrain_x - brush_width // 2
            start_y = terrain_y - brush_height // 2

            # Apply (blend) the brush to the heightmap.
            self.heightmap_image.blend_sub_image(
                brush_image,
                max(0, start_x),  # Clamp to ensure valid position.
                max(0, start_y),
                0,  # Brush offset X.
                0,  # Brush offset Y.
                min(brush_width, (self.heightmap_image.get_x_size() - start_x) * self.brush_size),  # Brush width.
                min(brush_height, (self.heightmap_image.get_y_size() - start_y) * self.brush_size)  # Brush height.
            )

            # Update the heightmap texture with the modified heightmap.
            self.heightmap_texture.load(self.heightmap_image)

            # Update the visual terrain mesh.
            self.terrain_node.heightfield = self.heightmap_texture
            self.terrain_node.generate()

            # Mark that a collision update is needed and set the updated area.
            self.collision_update_needed = True
            self.updated_area = (max(0, start_x), max(0, start_y), min(self.heightmap_image.get_x_size(), start_x + brush_width), min(self.heightmap_image.get_y_size(), start_y + brush_height))
        else:
            print("Click outside terrain bounds.")

    def enable_bullet_debug(self):
        debug_node = BulletDebugNode('Debug')
        debug_node.showWireframe(True)
        debug_node.showConstraints(True)
        debug_node.showBoundingBoxes(False)
        debug_node.showNormals(False)
        self.debug_np = self.world.render.attach_new_node(debug_node)
        self.terrain_collider.bullet_world.setDebugNode(self.debug_np.node())