import vtk
s=vtk.vtkSphereSource();s.SetThetaResolution(32);s.SetPhiResolution(24)
m=vtk.vtkPolyDataMapper();m.SetInputConnection(s.GetOutputPort());a=vtk.vtkActor();a.SetMapper(m);a.GetProperty().SetColor(.2,.4,.5)
r=vtk.vtkRenderer();r.AddActor(a);r.SetBackground(.9,.9,.9)
w=vtk.vtkRenderWindow();w.SetOffScreenRendering(1);w.AddRenderer(r);w.SetSize(500,400);r.ResetCamera();w.Render()
f=vtk.vtkWindowToImageFilter();f.SetInput(w);f.Update();out=vtk.vtkPNGWriter();out.SetFileName('model-renders/vtk-test.png');out.SetInputConnection(f.GetOutputPort());out.Write();print('VTK render succeeded')
