import networkx as nx
from .celery_app import celery_app
from app.websocket.manager import manager
import asyncio
from typing import List, Tuple
import numpy as np

@celery_app.task(bind=True)
def solve_tsp(self, points: List[Tuple[float, float]], user_id: str):
    """
    Solve TSP using a simple genetic algorithm with progress updates
    """
    # Create a complete graph
    G = nx.Graph()
    for i, point in enumerate(points):
        G.add_node(i, pos=point)
    
    # Add edges with distances
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            distance = np.sqrt((points[i][0] - points[j][0])**2 + (points[i][1] - points[j][1])**2)
            G.add_edge(i, j, weight=distance)

    # Simple genetic algorithm implementation
    population_size = 50
    generations = 100
    population = [list(np.random.permutation(len(points))) for _ in range(population_size)]
    
    for gen in range(generations):
        # Calculate fitness for each solution
        fitness = []
        for solution in population:
            total_distance = 0
            for i in range(len(solution)):
                total_distance += G[solution[i]][solution[(i + 1) % len(solution)]]['weight']
            fitness.append(1 / total_distance)
        
        # Select parents
        parents = []
        for _ in range(population_size):
            tournament = np.random.choice(len(population), 3, replace=False)
            winner = max(tournament, key=lambda x: fitness[x])
            parents.append(population[winner])
        
        # Create new population
        new_population = []
        for i in range(0, population_size, 2):
            parent1, parent2 = parents[i], parents[i + 1]
            # Crossover
            crossover_point = np.random.randint(1, len(points) - 1)
            child1 = parent1[:crossover_point] + [x for x in parent2 if x not in parent1[:crossover_point]]
            child2 = parent2[:crossover_point] + [x for x in parent1 if x not in parent2[:crossover_point]]
            
            # Mutation
            if np.random.random() < 0.1:
                idx1, idx2 = np.random.choice(len(points), 2, replace=False)
                child1[idx1], child1[idx2] = child1[idx2], child1[idx1]
            if np.random.random() < 0.1:
                idx1, idx2 = np.random.choice(len(points), 2, replace=False)
                child2[idx1], child2[idx2] = child2[idx2], child2[idx1]
            
            new_population.extend([child1, child2])
        
        population = new_population
        
        # Send progress update
        progress = int((gen + 1) / generations * 100)
        asyncio.run(manager.send_task_progress(user_id, self.request.id, progress))
    
    # Find best solution
    best_solution = min(population, key=lambda x: sum(G[x[i]][x[(i + 1) % len(x)]]['weight'] for i in range(len(x))))
    total_distance = sum(G[best_solution[i]][best_solution[(i + 1) % len(best_solution)]]['weight'] 
                        for i in range(len(best_solution)))
    
    # Add the starting point at the end to complete the cycle
    best_solution.append(best_solution[0])
    
    # Send completion message
    asyncio.run(manager.send_task_completed(user_id, self.request.id, best_solution, total_distance))
    
    return {
        'path': best_solution,
        'total_distance': total_distance
    }
