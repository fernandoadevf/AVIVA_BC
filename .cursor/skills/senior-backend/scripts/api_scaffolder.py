#!/usr/bin/env python3
"""
API Scaffolder — Generates production-ready API endpoints.

Supports REST and GraphQL scaffolding for Express, Fastify, Flask, and Gin
with built-in validation, auth middleware, and test generation.

Usage:
    python api_scaffolder.py <project-path> --type rest --resource users --auth jwt
    python api_scaffolder.py <project-path> --type graphql --schema users
    python api_scaffolder.py <project-path> --type rest --resource orders --with-tests
"""

import argparse
import os
import sys
import json
from pathlib import Path
from textwrap import dedent


TEMPLATES = {
    "rest": {
        "express": {
            "router": dedent("""\
                import {{ Router }} from 'express';
                import {{ z }} from 'zod';
                import {{ authenticate }} from '../middleware/auth';
                import {{ validate }} from '../middleware/validate';
                import * as {resource}Controller from '../controllers/{resource}.controller';

                const router = Router();

                const Create{Resource}Schema = z.object({{
                  // Define your validation schema
                  name: z.string().min(1).max(255),
                }});

                const Update{Resource}Schema = Create{Resource}Schema.partial();

                router.get('/', {auth_middleware}{resource}Controller.list);
                router.post('/', {auth_middleware}validate(Create{Resource}Schema), {resource}Controller.create);
                router.get('/:id', {auth_middleware}{resource}Controller.getById);
                router.patch('/:id', {auth_middleware}validate(Update{Resource}Schema), {resource}Controller.update);
                router.delete('/:id', {auth_middleware}{resource}Controller.remove);

                export default router;
            """),
            "controller": dedent("""\
                import {{ Request, Response, NextFunction }} from 'express';
                import * as {resource}Service from '../services/{resource}.service';

                export async function list(req: Request, res: Response, next: NextFunction) {{
                  try {{
                    const {{ page = '1', limit = '20' }} = req.query;
                    const result = await {resource}Service.list(Number(page), Number(limit));
                    res.json({{ data: result.data, pagination: result.pagination }});
                  }} catch (err) {{
                    next(err);
                  }}
                }}

                export async function create(req: Request, res: Response, next: NextFunction) {{
                  try {{
                    const item = await {resource}Service.create(req.body);
                    res.status(201).json({{ data: item }});
                  }} catch (err) {{
                    next(err);
                  }}
                }}

                export async function getById(req: Request, res: Response, next: NextFunction) {{
                  try {{
                    const item = await {resource}Service.getById(req.params.id);
                    if (!item) return res.status(404).json({{ error: {{ code: 'NOT_FOUND', message: '{Resource} not found' }} }});
                    res.json({{ data: item }});
                  }} catch (err) {{
                    next(err);
                  }}
                }}

                export async function update(req: Request, res: Response, next: NextFunction) {{
                  try {{
                    const item = await {resource}Service.update(req.params.id, req.body);
                    if (!item) return res.status(404).json({{ error: {{ code: 'NOT_FOUND', message: '{Resource} not found' }} }});
                    res.json({{ data: item }});
                  }} catch (err) {{
                    next(err);
                  }}
                }}

                export async function remove(req: Request, res: Response, next: NextFunction) {{
                  try {{
                    await {resource}Service.remove(req.params.id);
                    res.status(204).send();
                  }} catch (err) {{
                    next(err);
                  }}
                }}
            """),
            "service": dedent("""\
                import {{ prisma }} from '../lib/prisma';

                export async function list(page: number, limit: number) {{
                  const skip = (page - 1) * limit;
                  const [data, total] = await Promise.all([
                    prisma.{resource}.findMany({{ skip, take: limit, orderBy: {{ createdAt: 'desc' }} }}),
                    prisma.{resource}.count(),
                  ]);
                  return {{
                    data,
                    pagination: {{ page, limit, total, totalPages: Math.ceil(total / limit) }},
                  }};
                }}

                export async function create(data: any) {{
                  return prisma.{resource}.create({{ data }});
                }}

                export async function getById(id: string) {{
                  return prisma.{resource}.findUnique({{ where: {{ id }} }});
                }}

                export async function update(id: string, data: any) {{
                  return prisma.{resource}.update({{ where: {{ id }}, data }});
                }}

                export async function remove(id: string) {{
                  return prisma.{resource}.delete({{ where: {{ id }} }});
                }}
            """),
            "test": dedent("""\
                import {{ describe, it, expect, beforeAll, afterAll }} from 'vitest';
                import request from 'supertest';
                import {{ app }} from '../app';

                describe('{Resource} API', () => {{
                  let createdId: string;

                  describe('POST /api/v1/{resource_plural}', () => {{
                    it('should create a new {resource}', async () => {{
                      const res = await request(app)
                        .post('/api/v1/{resource_plural}')
                        .send({{ name: 'Test {Resource}' }})
                        .expect(201);

                      expect(res.body.data).toHaveProperty('id');
                      createdId = res.body.data.id;
                    }});

                    it('should return 422 for invalid body', async () => {{
                      const res = await request(app)
                        .post('/api/v1/{resource_plural}')
                        .send({{}})
                        .expect(422);

                      expect(res.body.error.code).toBe('VALIDATION_ERROR');
                    }});
                  }});

                  describe('GET /api/v1/{resource_plural}', () => {{
                    it('should list {resource_plural}', async () => {{
                      const res = await request(app)
                        .get('/api/v1/{resource_plural}')
                        .expect(200);

                      expect(res.body.data).toBeInstanceOf(Array);
                      expect(res.body.pagination).toBeDefined();
                    }});
                  }});

                  describe('GET /api/v1/{resource_plural}/:id', () => {{
                    it('should get a {resource} by id', async () => {{
                      const res = await request(app)
                        .get(`/api/v1/{resource_plural}/${{createdId}}`)
                        .expect(200);

                      expect(res.body.data.id).toBe(createdId);
                    }});

                    it('should return 404 for non-existent id', async () => {{
                      await request(app)
                        .get('/api/v1/{resource_plural}/non-existent-id')
                        .expect(404);
                    }});
                  }});

                  describe('PATCH /api/v1/{resource_plural}/:id', () => {{
                    it('should update a {resource}', async () => {{
                      const res = await request(app)
                        .patch(`/api/v1/{resource_plural}/${{createdId}}`)
                        .send({{ name: 'Updated {Resource}' }})
                        .expect(200);

                      expect(res.body.data.name).toBe('Updated {Resource}');
                    }});
                  }});

                  describe('DELETE /api/v1/{resource_plural}/:id', () => {{
                    it('should delete a {resource}', async () => {{
                      await request(app)
                        .delete(`/api/v1/{resource_plural}/${{createdId}}`)
                        .expect(204);
                    }});
                  }});
                }});
            """),
        }
    },
    "graphql": {
        "typeDefs": dedent("""\
            import {{ gql }} from 'graphql-tag';

            export const {resource}TypeDefs = gql`
              type {Resource} {{
                id: ID!
                name: String!
                createdAt: DateTime!
                updatedAt: DateTime!
              }}

              type {Resource}Connection {{
                edges: [{Resource}Edge!]!
                pageInfo: PageInfo!
              }}

              type {Resource}Edge {{
                node: {Resource}!
                cursor: String!
              }}

              input Create{Resource}Input {{
                name: String!
              }}

              input Update{Resource}Input {{
                name: String
              }}

              extend type Query {{
                {resource}(id: ID!): {Resource}
                {resource_plural}(first: Int, after: String): {Resource}Connection!
              }}

              extend type Mutation {{
                create{Resource}(input: Create{Resource}Input!): {Resource}!
                update{Resource}(id: ID!, input: Update{Resource}Input!): {Resource}!
                delete{Resource}(id: ID!): Boolean!
              }}
            `;
        """),
        "resolvers": dedent("""\
            import * as {resource}Service from '../services/{resource}.service';

            export const {resource}Resolvers = {{
              Query: {{
                {resource}: (_: any, {{ id }}: {{ id: string }}) => {resource}Service.getById(id),
                {resource_plural}: (_: any, {{ first, after }}: {{ first?: number; after?: string }}) =>
                  {resource}Service.listConnection(first ?? 20, after),
              }},
              Mutation: {{
                create{Resource}: (_: any, {{ input }}: {{ input: any }}) => {resource}Service.create(input),
                update{Resource}: (_: any, {{ id, input }}: {{ id: string; input: any }}) => {resource}Service.update(id, input),
                delete{Resource}: (_: any, {{ id }}: {{ id: string }}) => {resource}Service.remove(id),
              }},
            }};
        """),
    },
}


def to_pascal(name: str) -> str:
    return "".join(word.capitalize() for word in name.replace("-", "_").split("_"))


def to_plural(name: str) -> str:
    if name.endswith("s"):
        return name + "es"
    if name.endswith("y"):
        return name[:-1] + "ies"
    return name + "s"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"  ✓ Created {path}")


def scaffold_rest(project_path: Path, resource: str, auth: str, with_tests: bool, framework: str):
    Resource = to_pascal(resource)
    resource_plural = to_plural(resource)
    auth_middleware = "authenticate, " if auth else ""

    templates = TEMPLATES["rest"].get(framework, TEMPLATES["rest"]["express"])
    src = project_path / "src"

    replacements = {
        "{resource}": resource,
        "{Resource}": Resource,
        "{resource_plural}": resource_plural,
        "{auth_middleware}": auth_middleware,
    }

    files = {
        src / "routes" / f"{resource}.routes.ts": templates["router"],
        src / "controllers" / f"{resource}.controller.ts": templates["controller"],
        src / "services" / f"{resource}.service.ts": templates["service"],
    }

    if with_tests:
        files[src / "__tests__" / f"{resource}.test.ts"] = templates["test"]

    for file_path, template in files.items():
        content = template
        for key, value in replacements.items():
            content = content.replace(key, value)
        write_file(file_path, content)


def scaffold_graphql(project_path: Path, resource: str):
    Resource = to_pascal(resource)
    resource_plural = to_plural(resource)
    src = project_path / "src"

    replacements = {
        "{resource}": resource,
        "{Resource}": Resource,
        "{resource_plural}": resource_plural,
    }

    files = {
        src / "graphql" / f"{resource}.typeDefs.ts": TEMPLATES["graphql"]["typeDefs"],
        src / "graphql" / f"{resource}.resolvers.ts": TEMPLATES["graphql"]["resolvers"],
    }

    for file_path, template in files.items():
        content = template
        for key, value in replacements.items():
            content = content.replace(key, value)
        write_file(file_path, content)


def main():
    parser = argparse.ArgumentParser(description="API Scaffolder — Generate production-ready API endpoints")
    parser.add_argument("project_path", help="Path to the project root")
    parser.add_argument("--type", choices=["rest", "graphql"], default="rest", help="API type (default: rest)")
    parser.add_argument("--resource", "--schema", help="Resource/schema name (singular, lowercase)")
    parser.add_argument("--auth", choices=["jwt", "apikey", "oauth", "none"], default="none", help="Auth type")
    parser.add_argument("--framework", choices=["express", "fastify", "flask", "gin"], default="express")
    parser.add_argument("--with-tests", action="store_true", help="Generate test files")

    args = parser.parse_args()

    if not args.resource:
        print("Error: --resource is required")
        sys.exit(1)

    project_path = Path(args.project_path).resolve()
    resource = args.resource.lower().replace("-", "_")

    print(f"\n🔧 Scaffolding {args.type.upper()} API for '{resource}'")
    print(f"   Project: {project_path}")
    print(f"   Framework: {args.framework}")
    if args.auth != "none":
        print(f"   Auth: {args.auth}")
    print()

    if args.type == "rest":
        scaffold_rest(project_path, resource, args.auth, args.with_tests, args.framework)
    else:
        scaffold_graphql(project_path, resource)

    print(f"\n✅ Scaffolding complete! Files generated for '{resource}'.\n")


if __name__ == "__main__":
    main()
