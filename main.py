from models.vgg import *
from torchsummary import summary
from utils.data_loader import *

os.environ['CUDA_VISIBLE_DEVICES'] = '0'

if __name__ == "__main__":
    # initialize device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("[INFO]The device used by torch is {}.".format(device))

    # initialize VGG16 model
    model = VGGnet(in_channels=3, num_classes=6).to(device)

    # initialize train valid test dataset
    train_dataset = DDRDataset("./dataset/DR_grading", dataset_type="train")
    train_dataloader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    print("[INFO]The length of the train data is {}.".format(train_dataset.__len__()))

    valid_dataset = DDRDataset("./dataset/DR_grading", dataset_type="valid")
    valid_dataloader = DataLoader(valid_dataset, batch_size=32, shuffle=True)
    print("[INFO]The length of the valid data is {}.".format(valid_dataset.__len__()))

    test_dataset = DDRDataset("./dataset/DR_grading", dataset_type="test")
    test_dataloader = DataLoader(test_dataset, batch_size=32, shuffle=True)
    print("[INFO]The length of the test  data is {}.".format(test_dataset.__len__()))

    # print(model)
    # x = torch.randn(1, 3, 224, 224).to(device)
    # print(model(x).shape)
    # for name, param in model.named_parameters():
    #    print(name, param.size())
    # model.train()
    # model.eval()

    print("[INFO]The detail of the model :")
    summary(model, (3, 224, 224))
    print("[INFO]The detail of the model is shown above.")

    # prepare hyper parameters
    criterion = nn.CrossEntropyLoss()
    learning_rate = 1e-4
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # train
    val_acc_list = []
    for epoch in range(300):
        model.train()
        train_loss = 0.0
        for batch_idx, (data, target) in enumerate(train_dataloader):
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        # val
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for batch_idx, (data, target) in enumerate(valid_dataloader):
                data, target = data.to(device), target.to(device)
                output = model(data)
                _, predicted = torch.max(output.data, dim=1)
                total += target.size(0)
                correct += (predicted == target).sum().item()
        acc_val = correct / total
        val_acc_list.append(acc_val)

        # save model
        torch.save(model.state_dict(), "./outputs/last.pt")
        if acc_val == max(val_acc_list):
            torch.save(model.state_dict(), "./outputs/best.pt")
            print("[INFO]Save epoch {} model".format(epoch))

        print("[INFO]Epoch = {},  loss = {},  acc_val = {}".format(epoch, train_loss, acc_val))