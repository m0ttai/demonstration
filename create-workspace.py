import json
import kfp
import kfp.dsl as dsl

# ----- Variables -----
workspace_name = "notebook00"
workspace_image = "text_classification:v1.0"
pvc_name = "pvc99"
source_pvc = ""
pvc_size = "100Gi"
storage_class = "storage-class-nas"
jupyter_namespace = "anonymous"

# ----- Create Manifest (FlexClone) -----
def clone_manifest(pvc_name, storage_class, pvc_size, source_pvc, jupyter_namespace):
	manifest = '''
{
	"apiVersion": "v1",
	"kind": "PersistentVolumeClaim",
	"metadata": {
		"name": "dataset-workspace-''' + str(pvc_name) + '''",
		"namespace": "''' + str(jupyter_namespace) + '''",
		"annotations": {
			"trident.netapp.io/cloneFromPVC": "''' + str(source_pvc) + '''"
		}
	},
	"spec": {
		"accessModes": ["ReadWriteMany"],
		"storageClassName": "''' + str(storage_class) + '''",
		"resources": {
			"requests": {
				"storage": "''' + str(pvc_size) + '''"
			}
		}
	}
}
'''
	return manifest

@dsl.pipeline(
	name = "Create Workspace",
	description = "Create Workspace and Clone Volumes"
)

# ----- Create Workspace -----
def create_workspace(str = pvc_name, str = source_pvc, str = pvc_size, str = storage_class, str = jupyter_namespace, str = workspace_name, str = workspace_image):
	dataset_clone = dsl.ResourceOp(
		name = 'dataset-clone-for-workspace',
		k8s_resource = json.loads(clone_manifest(workspace_name, storage_class. pvc_size, source_pvc, jupyter_namespace)),
		action = 'create'
	)

	print_instructions = dsl.ContainerOp(
		name = str(workspace_name),
		image = str(workspace_image),
		command = ["sh", "-c"],
		arguments = ['echo "To deploy an interactive workspace, privision a new Jupyter workspace in namespace, ' + str(jupyter_namespace) + ', and mount dataset volume, dataset-workspace-' + str(workspace_name) + '."']
	)
	print_instructions.after(dataset_clone)

if __name__ == '__main__':
	kfp.compiler.Compiler().compile(create_workspace, __file__ + '.yaml')