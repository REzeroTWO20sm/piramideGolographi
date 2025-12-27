import pygame
import math
import sys

class ColorfullCubes:
    def __init__(self):
        pygame.init()
        
        self.front_matrix = []
        self.back_matrix = []
        self.left_matrix = []
        self.right_matrix = []


        # Настройки
        self.WINDOW_SIZE = 32
        self.TOTAL_WIDTH = self.WINDOW_SIZE * 2
        self.TOTAL_HEIGHT = self.WINDOW_SIZE * 2
        self.screen = pygame.display.set_mode((self.TOTAL_WIDTH, self.TOTAL_HEIGHT))
        pygame.display.set_caption("3D Cube - 4 Views")

        # Глобальная переменная для зума (используется в функциях)
        self.zoom_factor = 1  # Начальное значение

        # 4 поверхности для видов
        self.views = [
            pygame.Surface((self.WINDOW_SIZE, self.WINDOW_SIZE)),
            pygame.Surface((self.WINDOW_SIZE, self.WINDOW_SIZE)),
            pygame.Surface((self.WINDOW_SIZE, self.WINDOW_SIZE)),
            pygame.Surface((self.WINDOW_SIZE, self.WINDOW_SIZE))
        ]

        self.clock = pygame.time.Clock()
        self.BACKGROUND = (0, 0, 0)
        self.WHITE = (255, 255, 255)

        # Цвета граней
        self.FACE_COLORS = [
            (255, 50, 50),    # Красная - задняя
            (50, 255, 50),    # Зеленая - передняя
            (50, 50, 255),    # Синяя - нижняя
            (255, 255, 50),   # Желтая - верхняя
            (255, 128, 0),    # Оранжевая - левая
            (128, 0, 255)     # Фиолетовая - правая
        ]

        # Вершины куба
        self.vertices = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
        ]

        # Грани
        self.faces = [
            [0, 1, 2, 3],  # задняя
            [4, 5, 6, 7],  # передняя
            [0, 1, 5, 4],  # низ
            [2, 3, 7, 6],  # верх
            [0, 3, 7, 4],  # левая
            [1, 2, 6, 5]   # правая
        ]

        self.angle_x, self.angle_y, self.angle_z = 0, 0, 0

    def rotate_point(self, point, ax, ay, az):
        x, y, z = point
        
        cosx, sinx = math.cos(ax), math.sin(ax)
        y_rot = y * cosx - z * sinx
        z_rot = y * sinx + z * cosx
        y, z = y_rot, z_rot
        
        cosy, siny = math.cos(ay), math.sin(ay)
        x_rot = x * cosy + z * siny
        z_rot = -x * siny + z * cosy
        x, z = x_rot, z_rot
        
        cosz, sinz = math.cos(az), math.sin(az)
        x_rot = x * cosz - y * sinz
        y_rot = x * sinz + y * cosz
        x, y = x_rot, y_rot
        
        return [x, y, z]

    # Функция проекции с использованием глобального zoom_factor
    def get_view_projection(self, point, view_index):
        x, y, z = point
        center = self.WINDOW_SIZE // 2
        scale = self.zoom_factor  # Используем глобальную переменную
        
        if view_index == 0:  # FRONT
            proj_x = x * scale + center
            proj_y = -y * scale + center
            
        elif view_index == 1:  # BACK
            proj_x = -x * scale + center
            proj_y = -y * scale + center
            
        elif view_index == 2:  # LEFT SIDE
            proj_x = z * scale + center
            proj_y = -y * scale + center
            
        else:  # RIGHT SIDE
            proj_x = -z * scale + center
            proj_y = -y * scale + center
        
        return [int(proj_x), int(proj_y)]

    # Улучшенная функция для вычисления центра грани
    def get_face_center(self, face_indices, rotated_verts):
        center_x, center_y, center_z = 0, 0, 0
        for idx in face_indices:
            center_x += rotated_verts[idx][0]
            center_y += rotated_verts[idx][1]
            center_z += rotated_verts[idx][2]
        count = len(face_indices)
        return [center_x/count, center_y/count, center_z/count]

    # Функция для вычисления расстояния от грани до камеры
    def get_face_distance(self, face_center, view_index):
        if view_index == 0:  # FRONT: камера смотрит вдоль +Z
            return face_center[2]  # Чем больше Z, тем дальше
        
        elif view_index == 1:  # BACK: камера смотрит вдоль -Z
            return -face_center[2]  # Чем меньше Z, тем дальше
        
        elif view_index == 2:  # LEFT SIDE: камера смотрит вдоль +X
            return face_center[0]  # Чем больше X, тем дальше
        
        else:  # RIGHT SIDE: камера смотрит вдоль -X
            return -face_center[0]  # Чем меньше X, тем дальше

    # Отрисовка куба на поверхности
    def draw_cube_on_surface(self, surface, view_index, rotated_verts):
        surface.fill(self.BACKGROUND)
        
        # Вычисляем центры и расстояния для всех граней
        faces_with_data = []
        for i, face in enumerate(self.faces):
            center = self.get_face_center(face, rotated_verts)
            distance = self.get_face_distance(center, view_index)
            faces_with_data.append((distance, i, face, center))
        
        # Сортируем по расстоянию (от дальних к ближним)
        faces_with_data.sort(key=lambda x: x[0], reverse=True)
        
        # Рисуем все грани
        for distance, face_idx, face, center in faces_with_data:
            face_points = [self.get_view_projection(rotated_verts[idx], view_index) for idx in face]
            
            # Простая проверка - рисуем если есть хотя бы 3 различные точки
            points_set = set((p[0], p[1]) for p in face_points)
            if len(points_set) >= 3:
                pygame.draw.polygon(surface, self.FACE_COLORS[face_idx], face_points, 0)
                pygame.draw.polygon(surface, self.WHITE, face_points, 2)

    def changeZoom(self, zoom):
        if zoom:
            self.zoom_factor = min(15, self.zoom_factor + 0.5)
        else:
            self.zoom_factor = max(1, self.zoom_factor - 0.5)
    
    def get_led_matrices(self):
        # Создаем массивы для 4 перспектив
        self.front_matrix = []
        self.back_matrix = []
        self.left_matrix = []
        self.right_matrix = []
        
        # Собираем пиксели для front (левый верхний)
        for y in range(16):
            for x in range(16):
                color = self.screen.get_at((x, y))
                self.front_matrix.append([x, y, (color.r, color.g, color.b)])
        
        # Собираем пиксели для back (правый верхний)
        for y in range(16):
            for x in range(16, 32):
                color = self.screen.get_at((x, y))
                self.back_matrix.append([x - 16, y, (color.r, color.g, color.b)])
        
        # Собираем пиксели для left (левый нижний)
        for y in range(16, 32):
            for x in range(16):
                color = self.screen.get_at((x, y))
                self.left_matrix.append([x, y - 16, (color.r, color.g, color.b)])
        
        # Собираем пиксели для right (правый нижний)
        for y in range(16, 32):
            for x in range(16, 32):
                color = self.screen.get_at((x, y))
                self.right_matrix.append([x - 16, y - 16, (color.r, color.g, color.b)])

    def runCubes(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        angle_x, angle_y, angle_z = 0, 0, 0
                    elif event.key == pygame.K_UP:
                        self.zoom_factor = min(15, self.zoom_factor + 0.5)
                        print(f"Zoom increased to: {self.zoom_factor}")
                    elif event.key == pygame.K_DOWN:
                        self.zoom_factor = max(1, self.zoom_factor - 0.5)
                        print(f"Zoom decreased to: {self.zoom_factor}")
            
            # Обновление вращения
            self.angle_x += 0.008
            self.angle_y += 0.01
            self.angle_z += 0.006
            
            # Вращение вершин
            rotated_vertices = []
            for vertex in self.vertices:
                rotated_vertices.append(self.rotate_point(vertex, self.angle_x, self.angle_y, self.angle_z))
            
            # Отрисовка на 4 поверхностях
            for i in range(4):
                self.draw_cube_on_surface(self.views[i], i, rotated_vertices)
            
            # Очистка и вывод на основной экран
            self.screen.fill((20, 20, 40))
            self.screen.blit(self.views[0], (0, 0))                     # Front
            self.screen.blit(self.views[1], (self.WINDOW_SIZE, 0))           # Back
            self.screen.blit(self.views[2], (0, self.WINDOW_SIZE))           # Left side
            self.screen.blit(self.views[3], (self.WINDOW_SIZE, self.WINDOW_SIZE)) # Right side
            
            # Разделительные линии
            pygame.draw.line(self.screen, (40, 40, 60), (self.WINDOW_SIZE, 0), (self.WINDOW_SIZE, self.TOTAL_HEIGHT), 2)
            pygame.draw.line(self.screen, (40, 40, 60), (0, self.WINDOW_SIZE), (self.TOTAL_WIDTH, self.WINDOW_SIZE), 2)
            
            # Информация о зуме
            font = pygame.font.SysFont(None, 20)
            zoom_text = font.render(f"Zoom: {self.zoom_factor} (UP/DOWN to adjust)", True, (150, 150, 150))
            self.screen.blit(zoom_text, (10, self.TOTAL_HEIGHT - 25))
            
            pygame.display.flip()
            self.clock.tick(60)
            self.get_led_matrices()
            print(self.front_matrix)
        pygame.quit()
        sys.exit()
