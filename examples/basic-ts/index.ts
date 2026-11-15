import * as pulumi from "@pulumi/pulumi";
import * as openrouter from "@pulumi/openrouter";

const resource = new openrouter.Resource("Resource", { sampleAttribute: "attr" });

export const sampleAttribute = resource.sampleAttribute;
